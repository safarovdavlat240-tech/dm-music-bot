import telebot, os, yt_dlp, threading
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is alive"

user_links = {}

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🎵 Салом! Линки YouTube / TikTok / Insta фирист!")

@bot.message_handler(func=lambda m: True)
def get_link(m):
    url = m.text.strip()
    if "http" not in url:
        return
    user_links[m.chat.id] = url
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎬 Видео", callback_data="video"),
               InlineKeyboardButton("🎵 Мусиқа (MP3)", callback_data="audio"))
    bot.send_message(m.chat.id, f"Чӣ тавр гирам?\n{url}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    url = user_links.get(call.message.chat.id)
    if not url:
        return
    bot.edit_message_text("⏳ Зеркашӣ...", call.message.chat.id, call.message.message_id)
    try:
        if call.data == "video":
            opts = {'format': 'best', 'outtmpl': '%(title)s.%(ext)s'}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file = ydl.prepare_filename(info)
            with open(file, 'rb') as f:
                bot.send_video(call.message.chat.id, f, caption="🎬 Тайёр!")
        else:
            opts = {'format': 'bestaudio/best', 'outtmpl': '%(title)s.%(ext)s',
                    'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file = ydl.prepare_filename(info).rsplit('.',1)[0] + ".mp3"
                # агар номаш дигар бошад
                if not os.path.exists(file):
                    # файлро ҷустуҷӯ кун
                    for f in os.listdir('.'):
                        if f.endswith('.mp3'):
                            file = f
                            break
            with open(file, 'rb') as f:
                bot.send_audio(call.message.chat.id, f, title=info.get('title','Music'), caption="🎵 Тайёр!")
        os.remove(file)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Хато: {e}")

def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot).start()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
