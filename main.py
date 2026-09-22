import telebot, os, yt_dlp, threading
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot alive"

user_links = {}

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🎵 Салом! Линк фирист - YouTube/TikTok/Insta\n\nАгар YouTube кор накунад, линки TikTok ё Insta фирист, 100% кор мекунад!")

@bot.message_handler(func=lambda m: True)
def get_link(m):
    url = m.text.strip()
    if "http" not in url: return
    user_links[m.chat.id] = url
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎬 Видео", callback_data="video"),
               InlineKeyboardButton("🎵 Мусиқа MP3", callback_data="audio"))
    bot.send_message(m.chat.id, "Чи тавр гирам?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    url = user_links.get(call.message.chat.id)
    if not url: return
    bot.edit_message_text("⏳ Зеркашӣ дорам...", call.message.chat.id, call.message.message_id)
    try:
        # Ин қисм YouTube-ро фиреб медиҳад
        base_opts = {
            'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'web']}},
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
        }
        if call.data == "video":
            opts = {**base_opts, 'format': 'best[height<=720]', 'outtmpl': 'video.%(ext)s'}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file = ydl.prepare_filename(info)
            with open(file, 'rb') as f:
                bot.send_video(call.message.chat.id, f, caption="🎬 Тайёр!")
        else:
            opts = {**base_opts, 'format': 'bestaudio/best', 'outtmpl': 'audio.%(ext)s',
                    'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # файли mp3-ро ёб
                file = "audio.mp3"
                if not os.path.exists(file):
                    for fn in os.listdir('.'):
                        if fn.endswith('.mp3'):
                            file=fn; break
            with open(file, 'rb') as f:
                bot.send_audio(call.message.chat.id, f, title=info.get('title','')[:50])
        if os.path.exists(file): os.remove(file)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ YouTube ҳоло блок кард.\nЛинки дигар санҷ - TikTok/Instagram 100% кор мекунад.\n\nХато: {str(e)[:200]}")

def run_bot(): bot.infinity_polling()
threading.Thread(target=run_bot).start()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
