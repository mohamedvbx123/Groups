import telebot
import json
import os
from datetime import datetime
import requests
from pathlib import Path

# --- إعدادات أساسية ---
BOT_TOKEN = "7872128615:AAE1Pfj5owmrptdSCtlCBj4XuDrRS7FWtrU"
CHANNEL_ID = -1002741781909  # ID القناة

bot = telebot.TeleBot(BOT_TOKEN)

DATA_FILE = "groups.json"
IMAGE_DIR = "images"
MAX_MESSAGES = 20

# --- تأكد من وجود الملفات والمجلدات ---
Path(IMAGE_DIR).mkdir(exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# --- تحميل صورة افتراضية باسم الجروب ---
def download_placeholder_image(name):
    url = f"https://via.placeholder.com/150.png?text={name[:15].replace(' ', '+')}"
    filename = f"{IMAGE_DIR}/{datetime.utcnow().timestamp():.0f}.png"
    r = requests.get(url)
    with open(filename, "wb") as f:
        f.write(r.content)
    return filename

# --- تحميل البيانات الحالية من JSON ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# --- حفظ البيانات بعد التعديل ---
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- فحص التكرار ---
def link_exists(data, url):
    return any(entry["url"] == url for entry in data)

# --- المعالجة الرئيسية ---
def process_channel():
    updates = bot.get_updates()
    groups = load_data()
    added = 0

    for update in updates[::-1]:
        if not update.channel_post:
            continue

        msg = update.channel_post
        if msg.chat.id != CHANNEL_ID:
            continue

        text = msg.text.strip()
        if not text.startswith("https://chat.whatsapp.com/"):
            continue

        if link_exists(groups, text):
            print(f"🔁 الرابط مكرر: {text}")
            continue

        # بيانات افتراضية (ممكن نطوّرها لاحقًا)
        name = "جروب بدون اسم"
        description = "تمت إضافته تلقائيًا"
        group_type = "عام"
        image_path = download_placeholder_image(name)

        groups.insert(0, {
            "name": name,
            "description": description,
            "type": group_type,
            "url": text,
            "image": image_path.replace("\\", "/"),
            "date": datetime.utcnow().isoformat() + "Z"
        })

        added += 1
        print(f"✅ تمت إضافة: {text}")

        if added >= MAX_MESSAGES:
            break

    if added > 0:
        save_data(groups)
        print(f"📦 تم حفظ {added} جروب جديد.")
    else:
        print("📭 لا توجد روابط جديدة.")

# --- تنفيذ ---
if __name__ == "__main__":
    process_channel()
