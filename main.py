import telebot
from datetime import timedelta, timezone
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from config import TOKEN
import logging
import time

logging.basicConfig(level=logging.INFO)

# Telegram Bot Token
bot = telebot.TeleBot(token=TOKEN)

# Define Bangladesh Timezone (UTC+6)
BDT = timezone(timedelta(hours=6))

# Chat IDs to send the message to (you can hardcode or dynamically add these IDs)
subscribers = [-4616198859]  # Replace with actual chat IDs

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    logging.info(message.chat.id)
    bot.reply_to(message, "Hello, I am vinci, and I can wish you people on their birthdays.")

def get_bday_guys():
    df = pd.read_csv("data/Employee Database (PSC) - Sheet3.csv")
    d = pd.Timestamp.today()
    names = []
    for _, row in df.iterrows():
        row["BOD"] = pd.to_datetime(row["BOD"])
        if row["BOD"].month == d.month and row["BOD"].day == d.day:
            names.append(row["Names"])
    return names

def send_birthday_message():
    employees = get_bday_guys()

    if len(employees):
        message = f"Happy Birthday {" ".join(employees)} 🎁🎉"

        # Send message to all subscribers
        for chat_id in subscribers:
            try:
                bot.send_message(chat_id, message)
                logging.info(f"Sent: '{message}' to {chat_id}")
            except Exception as e:
                logging.info(f"Failed to send message to {chat_id}: {e}")
    else:
        logging.info(f"No birthdays today")

# Start the bot
if __name__ == '__main__':
    scheduler = BackgroundScheduler(timezone=BDT)
    scheduler.add_job(send_birthday_message, 'cron', hour=0, minute=0, misfire_grace_time=300)
    try:
        logging.info(f"Bot has started...")
        time.sleep(5)
        scheduler.start()
        bot.infinity_polling(interval=0, timeout=40)
    except Exception as e:
        logging.info(f"ERROR: {e}")