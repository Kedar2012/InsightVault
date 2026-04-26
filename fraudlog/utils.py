from django.core.cache import cache
from .models import FraudEventLog

def record_failed_login(user):
    key = f"failed_login:{user.id}"
    count = cache.get(key, 0) + 1
    cache.set(key, count, timeout=3600)  # expire in 1 hour

    if count >= 3:
        FraudEventLog.objects.create(
            user=user,
            event_type="failed_login_threshold",
            details={"attempts": count}
        )
    return count
