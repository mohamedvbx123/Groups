import telebot
import os
import json
import requests
from PIL import Image
from io import BytesIO

# إعدادات عامة
BOT_TOKEN = "7872128615:AAE1Pfj5owmrptdSCtlCBj4XuDrRS7FWtrU"
CHANNEL_ID = -1002741781909  # معرف القناة
JSON_FILE = "groups.json"
IMAGES_DIR = "images"
DEFAULT_IMAGE = f"{IMAGES_DIR}/default.png"

# إنشاء البوت
bot = telebot.TeleBot(BOT_TOKEN)

# تحديد التصنيف حسب الرابط
def detect_classification(url):
    url = url.lower()
    if "chat.whatsapp.com" in url:
        return "WhatsApp_group"
    elif "whatsapp.com/channel" in url:
        return "WhatsApp_channel"
    elif "t.me/" in url:
        return "Telegram"
    elif "facebook.com/groups" in url:
        return "Facebook_Group"
    elif "facebook.com" in url:
        return "Facebook_Page"
    else:
        return "strange"

# تحميل الصورة
def download_image(file_id, name_slug):
    try:
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        ext = file_info.file_path.split(".")[-1]
        image_name = f"{name_slug}.{ext}"
        image_path = os.path.join(IMAGES_DIR, image_name)
        with open(image_path, "wb") as f:
            f.write(file)
        return image_path
    except:
        return DEFAULT_IMAGE

# تنظيف الاسم للاستخدام كاسم صورة
def slugify(name):
    return "".join(c if c.isalnum() else "_" for c in name)[:30]

# قراءة البيانات القديمة
def load_data():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# حفظ البيانات
def save_data(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# معالجة الرسائل في القناة
def process_channel():
    updates = bot.get_updates()
    data = load_data()
    added_links = {entry["url"] for entry in data}

    for update in updates:
        if not update.message or update.message.chat.id != CHANNEL_ID:
            continue

        msg = update.message
        text = msg.text or ""
        photo = msg.photo[-1] if msg.photo else None

        name = ""
        description = ""
        gtype = ""
        url = ""

        for line in text.splitlines():
            line = line.strip()
            if line.lower().startswith("name:"):
                name = line[5:].strip()
            elif line.lower().startswith("description:"):
                description = line[12:].strip()
            elif line.lower().startswith("type:"):
                gtype = line[5:].strip()
            elif line.lower().startswith("url:"):
                url = line[4:].strip()

        if not url or url in added_links:
            continue

        classification = detect_classification(url)
        name_slug = slugify(name or "group")

        image_path = download_image(photo.file_id, name_slug) if photo else DEFAULT_IMAGE

        group_entry = {
            "name": name or "بدون اسم",
            "description": description or "لا يوجد وصف",
            "type": gtype or "غير محدد",
            "url": url,
            "image": image_path,
            "classification": classification
        }

        data.insert(0, group_entry)

    save_data(data)

# تنفيذ المعالجة
process_channel()
