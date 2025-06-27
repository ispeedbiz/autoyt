# utils.py
import os
import re
from datetime import datetime
from dotenv import load_dotenv
def load_env():
    load_dotenv('.env')  # <--- Use '.env' (not '../.env')
    env = {
        "OPENAI_API_KEY": os.environ["OPENAI_API_KEY"],
        "ELEVENLABS_API_KEY": os.environ["ELEVENLABS_API_KEY"],
        "TELEGRAM_BOT_TOKEN": os.environ.get("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.environ.get("TELEGRAM_CHAT_ID"),
    }
    return env

def sanitize_folder_name(text):
    return re.sub(r'[^a-zA-Z0-9_]+', '_', text)[:50]

def get_video_folder(base_folder, title, date_str=None):
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    safe_title = sanitize_folder_name(title)
    folder = os.path.join(base_folder, f"video_{date_str}_{safe_title}")
    os.makedirs(folder, exist_ok=True)
    return folder

def save_text_to_file(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def log_to_file(log_message, folder):
    log_file = os.path.join(folder, "logs.txt")
    with open(log_file, "a", encoding="utf-8") as logf:
        logf.write(f"{datetime.now().isoformat()} | {log_message}\n")

# Add more helpers as you go!
