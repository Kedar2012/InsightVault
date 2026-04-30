from pymongo import MongoClient
from django.conf import settings

def get_mongo_collection():
    client = MongoClient(
        host=settings.MONGO_DB["HOST"],
        port=settings.MONGO_DB["PORT"],
        username=settings.MONGO_DB["USER"],
        password=settings.MONGO_DB["PASSWORD"],
        authSource="admin",   # ✅ authenticate against admin
    )
    db = client[settings.MONGO_DB["NAME"]]   # target DB
    return db["fraud_event_logs"]            # collection name


def log_event(data: dict):
    collection = get_mongo_collection()
    result = collection.insert_one(data)
    return result.inserted_id