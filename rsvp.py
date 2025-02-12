# rsvp.py

# Dictionary to store RSVP responses
rsvp_data = {}

def handle_rsvp(bot, message, events_data):
    """Handles RSVP responses."""
    chat_id = message.chat.id
    try:
        _, event_id, response = message.text.split()
        response = response.lower()
        if response not in ['yes', 'no', 'maybe']:
            bot.send_message(chat_id, "❌ Invalid response. Please use yes, no, or maybe.")
            return
        creator_id, event_uuid = event_id.split('_')
        if int(creator_id) not in events_data or events_data[int(creator_id)].get('event_id') != event_id:
            bot.send_message(chat_id, "❌ Invalid event ID.")
            return
        if event_id not in rsvp_data:
            rsvp_data[event_id] = {}
        rsvp_data[event_id][chat_id] = response
        bot.send_message(chat_id, f"✅ Your RSVP '{response}' for event ID {event_id} has been recorded.")
        # Notify event creator
        bot.send_message(creator_id, f"\U0001F4E2 {message.from_user.username} has responded '{response}' to your event \"{events_data[int(creator_id)]['name']}\".")
    except ValueError:
        bot.send_message(chat_id, "❌ Invalid command format. Use /rsvp <event_id> <yes|no|maybe>.")