from pymongo import MongoClient
from django.conf import settings
from datetime import datetime


def get_mongo_collection():
    client = MongoClient(
        host=settings.MONGO_DB["HOST"],
        port=settings.MONGO_DB["PORT"],
        username=settings.MONGO_DB["USER"],
        password=settings.MONGO_DB["PASSWORD"],
        authSource="admin",
    )
    db = client[settings.MONGO_DB["NAME"]]
    return db["fraud_event_logs"]

def log_event(event_type, user_id, ip_address=None, device_info=None, extra=None):
    collection = get_mongo_collection()
    event = {
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "device_info": device_info,
        "extra": extra,
        "timestamp": datetime.utcnow(),
    }
    return collection.insert_one(event).inserted_id

def get_events(query=None):
    collection = get_mongo_collection()
    if query is None:
        query = {}
    return list(collection.find(query))