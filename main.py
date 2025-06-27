# main.py
import telebot
import requests
import json
import os
import re
from PIL import Image
from io import BytesIO
from datetime import datetime

# إعدادات البوت
BOT_TOKEN = "7872128615:AAE1Pfj5owmrptdSCtlCBj4XuDrRS7FWtrU"
CHANNEL_ID = -1002741781909  # آي دي القناة
JSON_FILE = "groups.json"
IMAGES_DIR = "images"
DEFAULT_IMAGE = "default.png"

bot = telebot.TeleBot(BOT_TOKEN)

# التأكد من وجود مجلد الصور
os.makedirs(IMAGES_DIR, exist_ok=True)

# تحميل صورة من تيليجرام
def download_telegram_image(file_id, name):
    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        ext = os.path.splitext(file_info.file_path)[1]
        filename = re.sub(r'\W+', '_', name.strip()) + ext
        path = os.path.join(IMAGES_DIR, filename)
        with open(path, 'wb') as new_file:
            new_file.write(downloaded_file)
        return path
    except Exception as e:
        print("[ERROR] Couldn't download image:", e)
        return os.path.join(IMAGES_DIR, DEFAULT_IMAGE)

# استخراج التصنيف بناءً على الرابط
def classify_url(url):
    if "t.me/" in url:
        return "Telegram"
    elif "facebook.com" in url:
        if "/groups/" in url:
            return "Facebook_Group"
        else:
            return "Facebook_Page"
    elif "chat.whatsapp.com" in url:
        return "WhatsApp_group"
    elif "whatsapp.com/channel" in url:
        return "WhatsApp_channel"
    else:
        return "strange"

# قراءة البيانات القديمة
try:
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
except:
    data = []

# استقبال الرسائل من القناة
@bot.channel_post_handler(content_types=['text', 'photo'])
def handle_channel_post(message):
    text = message.caption if message.content_type == 'photo' else message.text
    if not text:
        return

    name = description = group_type = url = None
    for line in text.splitlines():
        if line.lower().startswith("name:"):
            name = line[5:].strip()
        elif line.lower().startswith("description:"):
            description = line[12:].strip()
        elif line.lower().startswith("type:"):
            group_type = line[5:].strip()
        elif line.lower().startswith("url:"):
            url = line[4:].strip()

    if not url:
        print("[SKIPPED] No URL found.")
        return

    image_path = os.path.join(IMAGES_DIR, DEFAULT_IMAGE)
    if message.content_type == 'photo':
        photo = message.photo[-1]  # أعلى دقة
        image_path = download_telegram_image(photo.file_id, name or "group")

    new_entry = {
        "name": name or "جروب بدون اسم",
        "description": description or "لا يوجد وصف",
        "type": group_type or "عام",
        "url": url,
        "image": image_path.replace("\\", "/"),
        "classification": classify_url(url),
        "timestamp": datetime.utcnow().isoformat()
    }

    # منع التكرار
    if not any(entry['url'] == new_entry['url'] for entry in data):
        data.insert(0, new_entry)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[ADDED] {new_entry['name']}")
    else:
        print(f"[DUPLICATE] {new_entry['url']}")

print("[BOT STARTED] Listening for channel posts...")
bot.polling()
