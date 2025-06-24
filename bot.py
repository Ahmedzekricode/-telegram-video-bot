import telebot
import yt_dlp
import os
import uuid
import traceback
from telebot import types

bot = telebot.TeleBot("7754982899:AAEU5iiD7GMOlT9ti05dpamCoAMI_ZKfuWY")
user_links = {}
used_links = {}

@bot.message_handler(commands=['start'])
def start_msg(message):
    if message.chat.type != "private":
        return
    markup = types.InlineKeyboardMarkup()
    share_btn = types.InlineKeyboardButton("📲 شارك البوت", url="https://t.me/HamlhaBot")
    markup.add(share_btn)
    bot.send_message(message.chat.id, "👋 مرحبًا بك! أرسل رابط فيديو من YouTube أو TikTok أو Instagram.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def ask_download_type(message):
    if message.chat.type != "private":
        return
    url = message.text.strip()
    if url in used_links.get(message.chat.id, []):
        bot.send_message(message.chat.id, "🔁 لقد أرسلت هذا الرابط من قبل.")
        return
    user_links[message.chat.id] = url
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎬 فيديو", callback_data="video")
    btn2 = types.InlineKeyboardButton("🎧 صوت", callback_data="audio")
    markup.add(btn1, btn2)
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', '📹 فيديو')
            thumb = info.get('thumbnail')
            if thumb:
                bot.send_photo(message.chat.id, thumb, caption=f"🎥 {title}\n\n✅ اختر نوع التحميل:", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, f"🎥 {title}\n\n✅ اختر نوع التحميل:", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "❌ لم أتمكن من قراءة الرابط، تأكد أنه صالح.")

@bot.callback_query_handler(func=lambda call: True)
def handle_choice(call):
    url = user_links.get(call.message.chat.id)
    if not url:
        bot.send_message(call.message.chat.id, "❗ لا يوجد رابط محفوظ.")
        return
    choice = call.data
    bot.send_message(call.message.chat.id, "⏳ جاري التحميل...")
    try:
        if not os.path.exists("temp"):
            os.makedirs("temp")
        unique_id = str(uuid.uuid4())
        file_out = f"temp/{unique_id}.%(ext)s"
        ydl_opts = {}
        if choice == "video":
            ydl_opts = {'format': 'mp4', 'outtmpl': file_out}
        elif choice == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': file_out,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("temp"):
            full_path = os.path.join("temp", file)
            if file.startswith(unique_id):
                if os.path.getsize(full_path) < 49 * 1024 * 1024:
                    with open(full_path, 'rb') as f:
                        if choice == "video":
                            bot.send_video(call.message.chat.id, f)
                        else:
                            bot.send_audio(call.message.chat.id, f)
                else:
                    bot.send_message(call.message.chat.id, "⚠️ الملف كبير بزاف وما نقدرش نبعثه.")
                os.remove(full_path)
        if call.message.chat.id in used_links:
            used_links[call.message.chat.id].append(url)
        else:
            used_links[call.message.chat.id] = [url]
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ خطأ: {str(e)}")
        print(traceback.format_exc())

bot.polling()
