from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot

# Telegram bot initialization
bot = TeleBot("8042742527:AAFf694R7VSPd3C4GwAc7jmjWM5cgAJBUVk")

# Initializing the scheduler
scheduler = BackgroundScheduler()
scheduler.start()




# Function to send a reminder
def send_reminder(chat_id, event_name):
    """
    Sends a reminder to the specified Telegram chat.
    """
    bot.send_message(chat_id, f"🔔 Reminder: The event \"{event_name}\" starts in 1 hour!")


# Function to schedule a reminder
def schedule_reminder(chat_id, event_name, event_start_time):
    """
    Schedules a reminder 1 hour before the specified event start time.
    """
    reminder_time = event_start_time - timedelta(hours=1)  # Calculate reminder time
    scheduler.add_job(
        send_reminder,
        'date',
        run_date=reminder_time,
        args=[chat_id, event_name]
    )
    print(f"Reminder scheduled for \"{event_name}\" at {reminder_time}.")

