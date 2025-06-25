import telebot
import requests
import os
import uuid
from telebot import types

bot = telebot.TeleBot("7754982899:AAEU5iiD7GMOlT9ti05dpamCoAMI_ZKfuWY")
headers = {'User-Agent': 'Mozilla/5.0'}
user_links = {}

def get_direct_link(url, mode="video"):
    if "youtube.com" in url or "youtu.be" in url:
        api = "https://ytmate.ltd/en68/"
        r = requests.post(api, data={"url": url}, headers=headers)
        link = r.text.split('href="')[1].split('"')[0]
        return link
    elif "tiktok.com" in url:
        api = f"https://snaptik.app/action.php?url={url}"
        r = requests.get(api, headers=headers)
        link = r.text.split('value="')[1].split('"')[0]
        return link
    elif "instagram.com/reel" in url:
        api = f"https://snapinsta.app/action.php?url={url}"
        r = requests.get(api, headers=headers)
        link = r.text.split('href="')[1].split('"')[0]
        return link
    elif "facebook.com" in url:
        api = "https://fdown.net/download.php"
        r = requests.post(api, data={"URLz": url}, headers=headers)
        link = r.text.split('href="')[1].split('"')[0]
        return link
    elif "twitter.com" in url or "x.com" in url:
        api = "https://ssstwitter.com/api"
        r = requests.post(api, data={"url": url}, headers=headers)
        link = r.json()["url"]
        return link
    else:
        return None

def get_info_text(url):
    try:
        if "youtube.com" in url or "youtu.be" in url:
            r = requests.get(url, headers=headers)
            title = r.text.split('<title>')[1].split('</title>')[0]
            return f"📛 العنوان: {title}"
        return "📄 لم أتمكن من جلب العنوان."
    except:
        return "📄 لم أتمكن من جلب العنوان."

def get_filesize(url):
    try:
        r = requests.head(url, allow_redirects=True, headers=headers)
        return int(r.headers.get("Content-Length", 0))
    except:
        return 0

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📲 شارك البوت", url="https://t.me/HamlhaBot"))
    bot.send_message(message.chat.id, "👋 مرحبًا! أرسل رابط فيديو من YouTube أو TikTok أو Instagram أو Facebook أو Twitter.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    user_links[message.chat.id] = url
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🎬 فيديو", callback_data="video"),
        types.InlineKeyboardButton("🎧 MP3", callback_data="mp3")
    )
    markup.add(types.InlineKeyboardButton("📄 معرفة اسم الفيديو", callback_data="info"))
    bot.send_message(message.chat.id, "✅ اختر نوع العملية:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_choice(call):
    url = user_links.get(call.message.chat.id)
    if not url:
        bot.send_message(call.message.chat.id, "❗ لا يوجد رابط محفوظ.")
        return
    if call.data == "info":
        info = get_info_text(url)
        bot.send_message(call.message.chat.id, info)
        return
    bot.send_message(call.message.chat.id, "⏳ جاري التحميل...")
    try:
        link = get_direct_link(url)
        if not link:
            bot.send_message(call.message.chat.id, "❌ تعذر جلب الفيديو من المصدر. تأكد أن الرابط صحيح.")
            return
        size = get_filesize(link)
        if size < 49 * 1024 * 1024:
            r = requests.get(link, headers=headers)
            ext = "mp3" if call.data == "mp3" else "mp4"
            fname = f"temp_{uuid.uuid4()}.{ext}"
            with open(fname, "wb") as f:
                f.write(r.content)
            with open(fname, "rb") as f:
                if ext == "mp3":
                    bot.send_audio(call.message.chat.id, f)
                else:
                    bot.send_video(call.message.chat.id, f)
            os.remove(fname)
        else:
            bot.send_message(call.message.chat.id, f"⚠️ الفيديو حجمه كبير وما نقدروش نبعثوه مباشرة.\nرابط التحميل المباشر:\n{link}")
    except:
        bot.send_message(call.message.chat.id, "❌ تعذر جلب الفيديو من المصدر.")

bot.polling()
