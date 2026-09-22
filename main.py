import telebot, os, yt_dlp, threading
from flask import Flask
TOKEN=os.getenv("BOT_TOKEN")
bot=telebot.TeleBot(TOKEN)
app=Flask(__name__)
@app.route('/')
def home(): return "Bot is alive"
@bot.message_handler(commands=['start'])
def start(m): bot.send_message(m.chat.id,"🎵 Салом! Линк фирист!")
@bot.message_handler(func=lambda m: True)
def dl(m):
  if "http" not in m.text: return
  bot.send_message(m.chat.id,"⏳ Зеркашӣ...")
  try:
    with yt_dlp.YoutubeDL({'format':'best','outtmpl':'%(title)s.%(ext)s'}) as ydl:
      info=ydl.extract_info(m.text,download=True)
      file=ydl.prepare_filename(info)
    with open(file,'rb') as f: bot.send_video(m.chat.id,f)
    os.remove(file)
  except Exception as e: bot.send_message(m.chat.id,f"Хато {e}")
def run_bot(): bot.infinity_polling()
threading.Thread(target=run_bot).start()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
