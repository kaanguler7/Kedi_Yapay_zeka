import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "chat_history.log")

# klasör yoksa oluştur
os.makedirs(LOG_DIR, exist_ok=True)

def log_message(sender, message, character):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] ({character}) {sender}: {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)