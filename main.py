import telebot
import json
import os
from datetime import datetime
from pathlib import Path
import requests

# --- إعدادات أساسية ---
BOT_TOKEN = "7872128615:AAE1Pfj5owmrptdSCtlCBj4XuDrRS7FWtrU"
CHANNEL_ID = -1002741781909

bot = telebot.TeleBot(BOT_TOKEN)

DATA_FILE = "groups.json"
IMAGE_DIR = "images"
MAX_MESSAGES = 20

# --- تجهيز المجلدات والملفات ---
Path(IMAGE_DIR).mkdir(exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# --- تحميل البيانات من JSON ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# --- حفظ البيانات ---
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- فحص تكرار الرابط ---
def link_exists(data, url):
    return any(entry["url"] == url for entry in data)

# --- حفظ صورة تيليجرام من ملف ---
def save_telegram_image(file_id):
    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        ext = os.path.splitext(file_info.file_path)[-1]
        filename = f"{IMAGE_DIR}/{datetime.utcnow().timestamp():.0f}{ext}"
        with open(filename, 'wb') as f:
            f.write(downloaded_file)
        return filename.replace("\\", "/")
    except Exception as e:
        print(f"⚠️ خطأ أثناء تحميل الصورة: {e}")
        return f"{IMAGE_DIR}/default.png"

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

        if not msg.text:
            continue

        text = msg.text.strip()
        if not text.startswith("https://chat.whatsapp.com/"):
            continue

        if link_exists(groups, text):
            print(f"🔁 الرابط مكرر: {text}")
            continue

        # إعداد بيانات الجروب
        name = "جروب بدون اسم"
        description = "تمت إضافته تلقائيًا"
        group_type = "عام"

        # فحص وجود صورة مرفقة
        image_path = f"{IMAGE_DIR}/default.png"
        if msg.photo:
            # ناخد أكبر حجم للصورة
            file_id = msg.photo[-1].file_id
            image_path = save_telegram_image(file_id)

        # إضافة الجروب
        groups.insert(0, {
            "name": name,
            "description": description,
            "type": group_type,
            "url": text,
            "image": image_path,
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
