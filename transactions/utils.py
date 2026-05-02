import redis
from datetime import datetime

r = redis.Redis(host="localhost", port=6379, db=0)

def check_transaction_velocity(account_id, window_seconds=60, max_txns=5):
    key = f"txn_velocity:{account_id}"
    now = datetime.utcnow().timestamp()

    created = r.lpush(key, now)

    if created == 1:
        r.expire(key, window_seconds)

    timestamps = [float(ts.decode()) for ts in r.lrange(key, 0, -1)]
    recent = [ts for ts in timestamps if now - ts <= window_seconds]

    return len(recent) > max_txns

