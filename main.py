import telebot
from datetime import timedelta, timezone, datetime
import mysql.connector
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from config import TOKEN
import logging
import time
import os

load_dotenv()  # Load environment variables from .env

# Telegram Bot Token
bot = telebot.TeleBot(token=os.getenv('TOKEN'))

# Define Bangladesh Timezone (UTC+6)
BDT = timezone(timedelta(hours=6))

# Chat IDs to send the message to (you can hardcode or dynamically add these IDs)
subscribers = [-1001413972467]  # Replace with actual chat IDs
thread_id = 2833

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    logging.info(f"Message ID: {message.chat.id} Thread ID: {message.message_thread_id}")
    if message.message_thread_id == thread_id:
        bot.reply_to(message, "Hello, I am vinchi, and I can wish you people on their birthdays.")

def get_bday_guys():
    # Database connection parameters from .env
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT')),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME')
    }
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        # Fetch active employees with name and date_of_birth
        cursor.execute("SELECT name, date_of_birth FROM employee WHERE is_active is TRUE")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Database error: {e}")
        return []
    
    # Get current date in BDT
    d = datetime.now(BDT)
    names = []
    for row in rows:
        dob = row['date_of_birth']
        logging.info(f"Processing employee: {row['name']} with DOB: {dob}")
        # Skip if date_of_birth is None/NULL
        if dob is None:
            # logging.warning(f"Date of birth is NULL for employee: {row['name']}")
            continue
            
        # Convert to date object if it's a datetime or string
        if isinstance(dob, datetime):
            dob = dob.date()
        elif isinstance(dob, str):
            # Assuming string format is YYYY-MM-DD
            try:
                dob = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                # If format differs, try another common format
                try:
                    dob = datetime.strptime(dob, '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    logging.warning(f"Could not parse date of birth: {dob}")
                    continue
        # Check if birthday matches today's month and day
        if dob.month == d.month and dob.day == d.day:
            names.append(row['name'])
    return names

def send_birthday_message():
    employees = get_bday_guys()
    
    if len(employees):
        message = f"Happy Birthday {' '.join(employees)} 🎁🎉"
        
        # Send message to all subscribers
        for chat_id in subscribers:
            try:
                bot.send_message(chat_id, message, message_thread_id=thread_id)
                logging.info(f"Sent: '{message}' to {chat_id}")
            except Exception as e:
                logging.info(f"Failed to send message to {chat_id}: {e}")
    else:
        logging.info(f"No birthdays today")

@bot.message_handler(commands=['birthdays'])
def show_birthdays(message):
    if message.message_thread_id == thread_id:
        employees = get_bday_guys()
        if employees:
            bot.reply_to(message, f"Birthdays today: {', '.join(employees)}")
        else:
            bot.reply_to(message, "No birthdays today.")

# Start the bot
if __name__ == '__main__':
    scheduler = BackgroundScheduler(timezone=BDT)
    scheduler.add_job(send_birthday_message, 'cron', hour=0, minute=1, misfire_grace_time=300)
    try:
        logging.info(f"Bot has started...")
        time.sleep(5)
        scheduler.start()
        bot.infinity_polling(interval=0, timeout=40)
    except Exception as e:
        logging.info(f"ERROR: {e}")