import telebot
import yt_dlp
import os
import uuid
from telebot import types

bot = telebot.TeleBot("7754982899:AAEU5iiD7GMOlT9ti05dpamCoAMI_ZKfuWY")
user_links = {}
used_links = {}

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type != "private":
        return
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📲 شارك البوت", url="https://t.me/HamlhaBot")
    markup.add(btn)
    bot.send_message(message.chat.id, "👋 أرسل رابط فيديو من YouTube أو TikTok فقط.", reply_markup=markup)

@bot.message_handler(func=lambda msg: True)
def handle_link(msg):
    if msg.chat.type != "private":
        return
    url = msg.text.strip().split('?')[0]
    if "instagram.com" in url:
        bot.send_message(msg.chat.id, "⚠️ روابط Instagram غير مدعومة حالياً.")
        return
    if url in used_links.get(msg.chat.id, []):
        bot.send_message(msg.chat.id, "🔁 هذا الرابط استُعمل من قبل.")
        return
    user_links[msg.chat.id] = url
    markup = types.InlineKeyboardMarkup()
    vbtn = types.InlineKeyboardButton("🎬 فيديو", callback_data="video")
    abtn = types.InlineKeyboardButton("🎧 صوت", callback_data="audio")
    markup.add(vbtn, abtn)
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', '')
            thumb = info.get('thumbnail')
            if thumb:
                bot.send_photo(msg.chat.id, thumb, caption=f"🎥 {title}\n\n✅ اختر نوع التحميل:", reply_markup=markup)
            else:
                bot.send_message(msg.chat.id, f"🎥 {title}\n\n✅ اختر نوع التحميل:", reply_markup=markup)
    except:
        bot.send_message(msg.chat.id, "❌ تعذر قراءة الرابط. تأكد أنه صالح.")

@bot.callback_query_handler(func=lambda call: True)
def process_download(call):
    url = user_links.get(call.message.chat.id)
    if not url:
        bot.send_message(call.message.chat.id, "❗ لا يوجد رابط.")
        return
    choice = call.data
    bot.send_message(call.message.chat.id, "⏳ جاري التحميل...")
    try:
        if not os.path.exists("temp"):
            os.makedirs("temp")
        uid = str(uuid.uuid4())
        out = f"temp/{uid}.%(ext)s"
        ydl_opts = {'format': 'mp4', 'outtmpl': out} if choice == "video" else {
            'format': 'bestaudio/best',
            'outtmpl': out,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("temp"):
            path = os.path.join("temp", file)
            if file.startswith(uid):
                if os.path.getsize(path) < 49 * 1024 * 1024:
                    with open(path, 'rb') as f:
                        if choice == "video":
                            bot.send_video(call.message.chat.id, f)
                        else:
                            bot.send_audio(call.message.chat.id, f)
                else:
                    bot.send_message(call.message.chat.id, "⚠️ الملف كبير.")
                os.remove(path)
        used_links.setdefault(call.message.chat.id, []).append(url)
    except:
        bot.send_message(call.message.chat.id, "❌ فشل التحميل.")

bot.polling()
