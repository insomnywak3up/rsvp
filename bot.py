from telebot import TeleBot
from datetime import datetime
from reminder import schedule_reminder  # Import schedule_reminder from reminder.py

# Bot token from BotFather
bot = TeleBot("8042742527:AAFf694R7VSPd3C4GwAc7jmjWM5cgAJBUVk")

# Dictionary to temporarily store event data
events_data = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id,
        f"👋 Hello {message.from_user.first_name}! I'm the <b>RSVP</b> bot here to help you manage events and invitations.\n\n"
        "📅 <b>You can:</b> \n"
        "✔️ Create events (/createevent)\n"
        "✔️ Send invitations to friends\n"
        "✔️ Track guest lists (/myevents)\n"
        "✔️ Confirm attendance (/rsvp &lt;ID&gt;)\n"
        "✔️ /help for more information about bot\n\n"
        "🚀 <em> Let's get started! Use /createevent to create your first event! </em>",
        parse_mode='html'
    )

# /createevent command handler
@bot.message_handler(commands=['createevent'])
def create_event(message):
    """
    Starts the process of creating a new event.
    """
    chat_id = message.chat.id
    events_data[chat_id] = {}  # Initialize data for this user
    bot.send_message(chat_id, "📋 What is the name of the event?")
    bot.register_next_step_handler(message, set_event_name)


def set_event_name(message):
    """
    Handles the name of the event.
    """
    chat_id = message.chat.id
    events_data[chat_id]['name'] = message.text
    bot.send_message(chat_id, "🗓️ Please provide the date of the event (format: YYYY-MM-DD):")
    bot.register_next_step_handler(message, set_event_date)


def set_event_date(message):
    """
    Handles the date of the event.
    """
    chat_id = message.chat.id
    try:
        # Parse user input as a date
        date = datetime.strptime(message.text, "%Y-%m-%d").date()
        events_data[chat_id]['date'] = date
        bot.send_message(chat_id, "⏰ Please provide the time of the event (format: HH:MM):")
        bot.register_next_step_handler(message, set_event_time)
    except ValueError:
        bot.send_message(chat_id, "❌ Invalid date format. Please use YYYY-MM-DD.")
        bot.register_next_step_handler(message, set_event_date)


def set_event_time(message):
    """
    Handles the time of the event.
    """
    chat_id = message.chat.id
    try:
        # Parse user input as time
        time = datetime.strptime(message.text, "%H:%M").time()
        events_data[chat_id]['time'] = time

        # Combine name, date, and time for the event
        event_name = events_data[chat_id]['name']
        event_date = events_data[chat_id]['date']
        event_time = events_data[chat_id]['time']

        # Create datetime object for event start time
        event_start_time = datetime.combine(event_date, event_time)

        # Schedule the reminder using reminder.py
        schedule_reminder(chat_id, event_name, event_start_time)

        # Inform the user about successful event creation
        bot.send_message(chat_id, f"✅ Event \"{event_name}\" created for {event_date} at {event_time}.\n"
                                  f"🔔 Reminder set 1 hour before the event!")

    except ValueError:
        bot.send_message(chat_id, "❌ Invalid time format. Please use HH:MM.")
        bot.register_next_step_handler(message, set_event_time)


if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()


    # Expose the bot object for external use
    def get_bot():
        return bot

bot.polling(none_stop=True)