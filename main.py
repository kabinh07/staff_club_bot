import telebot
from datetime import datetime, timedelta, timezone
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

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

# Function to send birthday messages
def send_birthday_message():
    while True:
        # Get the current time in BDT
        now_bdt = datetime.now(BDT)
        current_date = now_bdt.strftime('%Y-%m-%d')

        # Check if today is a birthday
        if current_date in birthdays:
            message = birthdays[current_date]

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

# Command to add a new birthday (optional, to dynamically add birthdays)
@bot.message_handler(commands=['add_birthday'])
def add_birthday(message):
    try:
        _, date, name = message.text.split(' ', 2)
        birthdays[date] = f"Happy Birthday to {name}!"
        bot.reply_to(message, f"Birthday added for {name} on {date}!")
    except ValueError:
        bot.reply_to(message, "Invalid format. Use: /add_birthday YYYY-MM-DD Name")

# Start the bot
if __name__ == '__main__':
    print("Bot is running...")
    bot.polling(none_stop=True)

    # Run the birthday message sender in parallel
    # send_birthday_message()
    check_connected_channels()
