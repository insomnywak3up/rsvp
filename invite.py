import uuid

def generate_event_id_and_store(chat_id, events_data):
    """Generates a unique event ID and stores it in the event data."""
    event_id = f"{chat_id}_{uuid.uuid4().hex[:8]}"
    events_data[chat_id]['event_id'] = event_id
    return event_id

def invite_participants(bot, message, events_data):
    """Displays the event ID for the event."""
    chat_id = message.chat.id
    if chat_id not in events_data:
        bot.send_message(chat_id, "❌ You need to create an event first using /createevent.")
        return
    event_id = events_data[chat_id]['event_id']
    bot.send_message(chat_id, f"📋 Share this event ID with your invitees: {event_id}")