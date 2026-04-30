from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from fraudlog.utils import record_failed_login

count = 0

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    global count
    count += 1
    user_id = credentials.get("username")
    ip_address = request.META.get("REMOTE_ADDR")
    device_info = request.META.get("HTTP_USER_AGENT")

    if count >= 4:
        record_failed_login(user_id, ip_address, device_info)
