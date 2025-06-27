import telebot
import requests
import json
import os
import re
from datetime import datetime

BOT_TOKEN = "7872128615:AAE1Pfj5owmrptdSCtlCBj4XuDrRS7FWtrU"
CHANNEL_ID = -1002741781909  # ID القناة اللي بتبعت فيها المنشورات
JSON_FILE = "groups.json"
IMAGES_DIR = "images"
DEFAULT_IMAGE = "default.png"

bot = telebot.TeleBot(BOT_TOKEN)

# تأكد إن مجلد الصور موجود
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
        print("حدث خطأ في تحميل الصورة:", e)
        return os.path.join(IMAGES_DIR, DEFAULT_IMAGE)

# قراءة ملف JSON
try:
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
except:
    data = []

from telebot.types import Message

# معالجة الرسائل من القناة
def process_channel():
    updates = bot.get_updates()
    new_messages = []

    for update in updates:
        if not update.message or update.message.chat.id != CHANNEL_ID:
            continue
        msg: Message = update.message
        if msg.date < datetime.utcnow().timestamp() - 86400:
            continue
        new_messages.append(msg)

    for message in new_messages:
        text = message.caption if message.content_type == 'photo' else message.text
        if not text:
            continue

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

        if not url or "chat.whatsapp.com" not in url:
            continue

        image_path = os.path.join(IMAGES_DIR, DEFAULT_IMAGE)
        if message.content_type == 'photo':
            photo = message.photo[-1]
            image_path = download_telegram_image(photo.file_id, name or "group")

        new_entry = {
            "name": name or "جروب بدون اسم",
            "description": description or "لا يوجد وصف",
            "type": group_type or "عام",
            "url": url,
            "image": image_path.replace("\\", "/")
        }

        if not any(entry['url'] == new_entry['url'] for entry in data):
            data.insert(0, new_entry)
            print(f"[ADDED] {new_entry['name']}")
        else:
            print(f"[SKIPPED - موجود مسبقًا] {new_entry['url']}")

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("[✅] العملية انتهت")

process_channel()
