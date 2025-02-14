import threading
import time
from datetime import datetime

def schedule_reminder(chat_id, event_name, event_time, bot):
    def remind():
        wait_time = (event_time - datetime.now()).total_seconds() - 3600
        if wait_time > 0:
            time.sleep(wait_time)
            bot.send_message(chat_id, f"⏰ Reminder: '{event_name}' starts in 1 hour!")
    thread = threading.Thread(target=remind)
    thread.start()