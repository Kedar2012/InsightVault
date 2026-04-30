from fraudlog.mongo_client import get_mongo_collection
from datetime import datetime

def record_failed_login(user_id, ip_address, device_info):
    collection = get_mongo_collection()
    event = {
        "event_type": "failed_login",
        "user_id": user_id,
        "ip_address": ip_address,
        "device_info": device_info,
        "timestamp": datetime.utcnow(),
    }
    collection.insert_one(event)
