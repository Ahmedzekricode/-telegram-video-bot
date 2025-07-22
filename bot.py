import os
import asyncio
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7741018335:AAFxSfAo_bF5dQ4gNLZod93J_powb44Tpus"

ydl_opts = {
    'format': 'best',
    'outtmpl': '%(title)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك!\n\n📥 أرسل رابط فيديو من YouTube أو TikTok أو Instagram وسأقوم بتحميله لك ✅"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("⚠️ الرجاء إرسال رابط صحيح!")
        return

    msg = await update.message.reply_text("⏳ جاري التحميل... انتظر قليلاً")

    try:
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        file_size = os.path.getsize(filename)

        
        if file_size > 49 * 1024 * 1024:  
            await msg.edit_text(f"📹 تم التحميل!\nلكن الفيديو أكبر من 50MB\nعنوان الفيديو: {info['title']}\nرابط مباشر: {info['webpage_url']}")
        else:
            await update.message.reply_video(video=open(filename, 'rb'), caption=f"✅ {info['title']}")

        os.remove(filename)

    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ: {e}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
