from datetime import timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot
from config import BOT_TOKEN

bot = TeleBot(BOT_TOKEN)
scheduler = BackgroundScheduler()
scheduler.start()

def send_reminder(chat_id, event_name):
    bot.send_message(chat_id, f"🔔 Reminder: The event \"{event_name}\" starts in 1 hour!")

def schedule_reminder(chat_id, event_name, event_start_time):
    reminder_time = event_start_time - timedelta(hours=1)
    scheduler.add_job(send_reminder, 'date', run_date=reminder_time, args=[chat_id, event_name])
    print(f"Reminder scheduled for \"{event_name}\" at {reminder_time}.")

