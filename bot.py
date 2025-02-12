import telebot
from datetime import datetime
from reminder import schedule_reminder  # Import schedule_reminder from reminder.py
from config import BOT_TOKEN  # Import token from config.py
from rsvp import handle_rsvp  # Import RSVP handlers
from invite import generate_event_id_and_store, invite_participants  # Import invite functions

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Dictionary to temporarily store event data
events_data = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id,
        f"\U0001F44B Hello {message.from_user.first_name}! I'm the <b>RSVP</b> bot here to help you manage events and invitations.\n\n"
        "\U0001F4C5 <b>You can:</b> \n"
        "✔️ Create events (/createevent)\n"
        "✔️ View your events (/myevents)\n"
        "✔️ Confirm attendance (/rsvp ID Response)\n"  # Clarified response format
        "✔️ /help for more information\n\n"
        "\U0001F680 <em>Let's get started! Use /createevent to create your first event!</em>",
        parse_mode='html'
    )

@bot.message_handler(commands=['createevent'])
def create_event(message):
    """Starts the process of creating a new event."""
    chat_id = message.chat.id
    events_data[chat_id] = {}  # Initialize data for this user
    bot.send_message(chat_id, "\U0001F4CB What is the name of the event?")
    bot.register_next_step_handler(message, set_event_name)

def set_event_name(message):
    """Handles the name of the event."""
    chat_id = message.chat.id
    events_data[chat_id]['name'] = message.text
    bot.send_message(chat_id, "\U0001F4C5 Please provide the date of the event (format: YYYY-MM-DD):")
    bot.register_next_step_handler(message, set_event_date)

def set_event_date(message):
    """Handles the date of the event."""
    chat_id = message.chat.id
    try:
        date = datetime.strptime(message.text, "%Y-%m-%d").date()
        events_data[chat_id]['date'] = date
        bot.send_message(chat_id, "\U000023F0 Please provide the time of the event (format: HH:MM):")
        bot.register_next_step_handler(message, set_event_time)
    except ValueError:
        bot.send_message(chat_id, "❌ Invalid date format. Please use YYYY-MM-DD.")
        bot.register_next_step_handler(message, set_event_date)

def set_event_time(message):
    """Handles the time of the event."""
    chat_id = message.chat.id
    try:
        time = datetime.strptime(message.text, "%H:%M").time()
        events_data[chat_id]['time'] = time

        # Combine name, date, and time
        event_name = events_data[chat_id]['name']
        event_date = events_data[chat_id]['date']
        event_time = events_data[chat_id]['time']
        event_start_time = datetime.combine(event_date, event_time)

        # Schedule reminder
        schedule_reminder(chat_id, event_name, event_start_time)

        # Generate event ID and store it
        event_id = generate_event_id_and_store(chat_id, events_data)

        bot.send_message(chat_id, f"✅ Event \"{event_name}\" created for {event_date} at {event_time}.\n"
                                  f"🔔 Reminder set 1 hour before the event!\n"
                                  f"📋 You can now invite participants. Share this event ID with them: {event_id}")
    except ValueError:
        bot.send_message(chat_id, "❌ Invalid time format. Please use HH:MM.")
        bot.register_next_step_handler(message, set_event_time)

@bot.message_handler(commands=['invite'])
def invite_command(message):
    """Handles the invite command."""
    invite_participants(bot, message, events_data)

@bot.message_handler(commands=['rsvp'])
def rsvp_command(message):
    """Handles the RSVP command."""
    handle_rsvp(bot, message, events_data)

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()

# Function to expose bot instance for external use
def get_bot():
    return bot