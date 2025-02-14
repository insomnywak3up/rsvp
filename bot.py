import telebot
from datetime import datetime
from reminder import schedule_reminder  # Import reminders
from config import BOT_TOKEN  # Bot token
from rsvp import handle_rsvp  # RSVP handler
from invite import generate_event_link, generate_event_id_and_store, invite_participants # Invitation functions
from events import list_events, cancel_event, edit_event  # Event listing, cancellation, and editing

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Dictionary to store event data
events_data = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id,
        f"👋 Hello, {message.from_user.first_name}! I am the <b>RSVP</b> bot to help you manage events.\n\n"
        "📅 <b>Features:</b> \n"
        "✔️ Create an event (/createevent)\n"
        "✔️ View my events (/myevents)\n"
        "✔️ Confirm attendance (/rsvp ID yes/no/maybe)\n"
        "✔️ Cancel an event (/cancel ID)\n"
        "✔️ Edit an event's date and time (/edit ID)\n"
        "🚀 <em>Start with /createevent!</em>",
        parse_mode='html'
    )

@bot.message_handler(commands=['createevent'])
def create_event(message):
    """Starts the event creation process."""
    chat_id = message.chat.id
    events_data[chat_id] = {}  # Initialize data
    bot.send_message(chat_id, "📋 What is the name of the event?")
    bot.register_next_step_handler(message, set_event_name)

def set_event_name(message):
    """Saves the event name."""
    chat_id = message.chat.id
    events_data[chat_id]['name'] = message.text
    bot.send_message(chat_id, "📅 Enter the date of the event (format: YYYY-MM-DD):")
    bot.register_next_step_handler(message, set_event_date)

def set_event_date(message):
    """Saves the event date."""
    chat_id = message.chat.id
    try:
        date = datetime.strptime(message.text, "%Y-%m-%d").date()
        events_data[chat_id]['date'] = date
        bot.send_message(chat_id, "⏰ Enter the time of the event (format: HH:MM):")
        bot.register_next_step_handler(message, set_event_time)
    except ValueError:
        bot.send_message(chat_id, "❌ Invalid date format. Use YYYY-MM-DD.")
        bot.register_next_step_handler(message, set_event_date)

def set_event_time(message):
    """Saves the event time and creates a link to Google Calendar."""
    chat_id = message.chat.id
    try:
        time = datetime.strptime(message.text, "%H:%M").time()
        events_data[chat_id]['time'] = time

        event_name = events_data[chat_id]['name']
        event_date = events_data[chat_id]['date']
        event_time = events_data[chat_id]['time']
        event_start_time = datetime.combine(event_date, event_time)

        # Generate event ID
        event_id = generate_event_id_and_store(chat_id, events_data)

        # Generate event link
        event_link = generate_event_link(event_name, event_start_time)

        # Send information to the user
        bot.send_message(chat_id, f"✅ Event \"{event_name}\" created!\n"
                                  f"📆 {event_date} at {event_time}\n"
                                  f"🔔 Reminder set!\n"
                                  f"📋 Event ID: {event_id}\n"
                                  f"🌍 <a href='{event_link}'>View in Google Calendar</a>",
                         parse_mode="HTML")
    except ValueError:
        bot.send_message(chat_id, "❌ Invalid time format. Use HH:MM.")
        bot.register_next_step_handler(message, set_event_time)

@bot.message_handler(commands=['myevents'])
def my_events_command(message):
    """Handles the myevents command."""
    chat_id = message.chat.id
    events = list_events(chat_id, events_data)
    if not events:
        bot.send_message(chat_id, "❌ No upcoming events found.")
    else:
        message_text = "📅 Your upcoming events:\n"
        for event in events:
            message_text += f"ID: {event['id']}\n"
            message_text += f"Name: {event['name']}\n"
            message_text += f"Date: {event['date']}\n"
            message_text += f"Time: {event['time']}\n"
            message_text += "----------------------\n"
        bot.send_message(chat_id, message_text)

@bot.message_handler(commands=['cancel'])
def cancel_event_command(message):
    """Handles the cancel command."""
    chat_id = message.chat.id
    try:
        _, event_id = message.text.split()
        result = cancel_event(chat_id, event_id, events_data)
        if result:
            bot.send_message(chat_id, f"✅ Event {event_id} has been canceled.")
        else:
            bot.send_message(chat_id, "❌ Invalid event ID or you don't have permission to cancel this event.")
    except ValueError:
        bot.send_message(chat_id, "❌ Invalid format. Use /cancel <event_id>.")

@bot.message_handler(commands=['edit'])
def edit_event_command(message):
    """Handles the edit command."""
    chat_id = message.chat.id
    try:
        _, event_id = message.text.split()
        if event_id in events_data['events'] and events_data['events'][event_id]['chat_id'] == chat_id:
            bot.send_message(chat_id, "📅 Enter the new date of the event (format: YYYY-MM-DD):")
            bot.register_next_step_handler(message, set_new_event_date, event_id)
        else:
            bot.send_message(chat_id, "❌ Invalid event ID or you don't have permission to edit this event.")
    except ValueError:
        bot.send_message(chat_id, "❌ Invalid format. Use /edit <event_id>.")

def set_new_event_date(message, event_id):
    """Saves the new event date."""
    chat_id = message.chat.id
    try:
        date = datetime.strptime(message.text, "%Y-%m-%d").date()
        events_data['events'][event_id]['date'] = date
        bot.send_message(chat_id, "⏰ Enter the new time of the event (format: HH:MM):")
        bot.register_next_step_handler(message, set_new_event_time, event_id)
    except ValueError:
        bot.send_message(chat_id, "❌ Invalid date format. Use YYYY-MM-DD.")
        bot.register_next_step_handler(message, set_new_event_date, event_id)

def set_new_event_time(message, event_id):
    """Saves the new event time and updates the event."""
    chat_id = message.chat.id
    try:
        time = datetime.strptime(message.text, "%H:%M").time()
        events_data['events'][event_id]['time'] = time

        event = events_data['events'][event_id]
        event_name = event['name']
        event_date = event['date']
        event_time = event['time']
        event_start_time = datetime.combine(event_date, event_time)

        # Generate new event link
        event_link = generate_event_link(event_name, event_start_time)

        # Update reminder
        schedule_reminder(chat_id, event_name, event_start_time, bot)

        # Send updated information to the user
        bot.send_message(chat_id, f"✅ Event \"{event_name}\" updated!\n"
                                  f"📆 New date: {event_date} at {event_time}\n"
                                  f"🔔 Reminder updated!\n"
                                  f"🌍 <a href='{event_link}'>View in Google Calendar</a>",
                         parse_mode="HTML")
    except ValueError:
        bot.send_message(chat_id, "❌ Invalid time format. Use HH:MM.")
        bot.register_next_step_handler(message, set_new_event_time, event_id)

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

def get_bot():
    return bot