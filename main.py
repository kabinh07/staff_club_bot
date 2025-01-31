import telebot
from datetime import datetime, timedelta, timezone
import time
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# Telegram Bot Token
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(token=TOKEN)

# Define Bangladesh Timezone (UTC+6)
BDT = timezone(timedelta(hours=6))

# List of birthdays: { "YYYY-MM-DD": "Name or Message" }
birthdays = {
    "2025-01-24": "Happy Birthday to John!",
    "2025-01-25": "Happy Birthday to Jane!",
    "2025-02-01": "Happy Birthday to Alice!"
}

# Chat IDs to send the message to (you can hardcode or dynamically add these IDs)
subscribers = [123456789, 987654321]  # Replace with actual chat IDs

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

# Function to send birthday messages
def check_connected_channels():
    updates = bot.get_updates()
    print(updates)
    group_chat_ids = set()
    groups = []
    for update in updates:
        if update.message and update.message.chat.type in ['group', 'supergroup']:
            group_chat_ids.add(update.message.chat.id)
    for id in group_chat_ids:
        try:
            status = bot.get_chat_member(chat_id=id, user_id=bot.get_me().id)
            if str(status.status) != "kicked":
                groups.append(id)
        except Exception as e:
            print(f"Telebot: {e}")
    print(groups)

def send_birthday_message():
    while True:
        # Get the current time in BDT
        now_bdt = datetime.now(BDT)
        employees = get_bday_guys()

        if len(employees):
            message = f"Happy Birthday {" ".join(employees)}"

            # Send message to all subscribers
            for chat_id in subscribers:
                try:
                    bot.send_message(chat_id, message)
                    print(f"Sent: '{message}' to {chat_id}")
                except Exception as e:
                    print(f"Failed to send message to {chat_id}: {e}")

            # Wait until the next day to avoid sending duplicate messages
            time_to_next_day = 24 - now_bdt.hour
            sleep_time = time_to_next_day * 3600
            print(f"Waiting for the next day... ({time_to_next_day} hours)")
            time.sleep(sleep_time)
        else:
            # Sleep for an hour and check again
            time.sleep(3600)

def get_bday_guys():
    df = pd.read_csv("data/Employee Database (PSC) - Sheet3.csv")
    print(df.head(10))
    d = pd.Timestamp.today()
    names = []
    for _, row in df.iterrows():
        row["BOD"] = pd.to_datetime(row["BOD"])
        if row["BOD"].month == d.month and row["BOD"].day == d.day:
            names.append(row["Names"])
    return names

# Start the bot
if __name__ == '__main__':
    # bot.infinity_polling(interval=0, timeout=20)
    check_connected_channels()
    
