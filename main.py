import telebot, os, yt_dlp
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🎵 Салом! Линки TikTok / YouTube фирист!")
@bot.message_handler(func=lambda x: True)
def dl(m):
    url = m.text.strip()
    if "http" not in url: return
    bot.send_message(m.chat.id, "⏳ Зеркашӣ...")
    try:
        opts = {'format':'best','outtmpl':'%(title)s.%(ext)s','quiet':True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)
        with open(file, 'rb') as f:
            bot.send_video(m.chat.id, f, caption=f"✅ {info.get('title')}")
        os.remove(file)
    except Exception as e:
        bot.send_message(m.chat.id, f"❌ Хато: {e}")
bot.infinity_polling()
