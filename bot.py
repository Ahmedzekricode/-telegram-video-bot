import os
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
import tempfile


api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

app = Client(
    "telegram-video-bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

async def download_video_and_send(url: str, message: Message):
    download_message = await message.reply_text("جاري التحميل...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'progress_hooks': [lambda d: print(d['status'])] 
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filepath = ydl.prepare_filename(info)

            file_size = os.path.getsize(filepath)
            
            if file_size > 50 * 1024 * 1024:  
                await download_message.edit_text("الملف كبير جداً، لا يمكن رفعه مباشرة، سيتم إرسال رابط.")
                caption = f"🔗 رابط الفيديو: [{info.get('title', 'الفيديو')}]({info['webpage_url']})"
                await message.reply_text(caption, disable_web_page_preview=False)
            else:
                caption = f"🎬 {info.get('title', 'الفيديو')} بواسطة AhmedZikoCode"
                await message.reply_video(filepath, caption=caption)
                await download_message.delete()

    except Exception as e:
        await download_message.edit_text(f"حدث خطأ: {e}")

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text("أهلاً بك! أرسل لي رابط فيديو من YouTube أو TikTok أو Instagram وسأقوم بتحميله لك.")

@app.on_message(filters.regex(r"(https?://)?(www\.)?(youtube\.com|youtu\.be|tiktok\.com|instagram\.com|x\.com)/[^\s]+"))
async def video_link_handler(client: Client, message: Message):
    url = message.text
    await download_video_and_send(url, message)

if __name__ == "__main__":
    app.run()
