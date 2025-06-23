import telebot
import json
import os
from datetime import datetime
import requests
from pathlib import Path

# إعدادات أساسية
BOT_TOKEN = "7872128615:AAE1Pfj5owmrptdSCtlCBj4XuDrRS7FWtrU"
OWNER_ID = 6177409979  # فقط هذا المستخدم مسموح له

bot = telebot.TeleBot(BOT_TOKEN)

DATA_FILE = "groups.json"
IMAGE_DIR = "images"

# تأكد من وجود الملف والمجلد
Path(IMAGE_DIR).mkdir(exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# تحميل صورة افتراضية مؤقتًا لأي جروب
def download_placeholder_image(name):
    url = "https://via.placeholder.com/150.png?text=" + name[:15]
    filename = f"{IMAGE_DIR}/{datetime.utcnow().timestamp():.0f}.png"
    r = requests.get(url)
    with open(filename, "wb") as f:
        f.write(r.content)
    return filename

# إضافة الجروب إلى JSON
def add_group_to_json(name, description, group_type, url, image_path):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        groups = json.load(f)

    groups.insert(0, {
        "name": name,
        "description": description,
        "type": group_type,
        "url": url,
        "image": image_path.replace("\\", "/"),
        "date": datetime.utcnow().isoformat() + "Z"
    })

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)

# التعامل مع الرسائل
@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "🚫 غير مسموح لك باستخدام هذا البوت.")
        return

    text = message.text.strip()
    if text.startswith("https://chat.whatsapp.com/"):
        bot.reply_to(message, "⏳ جاري معالجة الرابط...")

        # اسم ووصف تجريبيين — ممكن تعدلهم يدوي لاحقًا
        name = "جروب واتساب"
        description = "تمت إضافة هذا الجروب تلقائيًا"
        group_type = "عام"  # لاحقًا هتعدلها يدوي

        image_path = download_placeholder_image(name)
        add_group_to_json(name, description, group_type, text, image_path)

        bot.send_message(message.chat.id, "✅ تم إضافة الجروب إلى الملف بنجاح")
    else:
        bot.reply_to(message, "❌ أرسل رابط جروب واتساب بصيغة: https://chat.whatsapp.com/...")
