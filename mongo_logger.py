from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from flask import session

# Ortam değişkenlerini yükle
load_dotenv()

# MongoDB bağlantısını kur
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["eclabre"]
messages = db["messages"]

def log_message(sender, message, character=None):
    doc = {
        "timestamp": datetime.utcnow(),
        "session_id": session.get("session_id", "anonim"),
        "sender": sender,
        "message": message,
        "character": character if sender == "Éćlabré" else None
    }

    try:
        messages.insert_one(doc)
        print("✅ MongoDB kaydedildi:", doc)
    except Exception as e:
        print("❌ MongoDB hata:", e)