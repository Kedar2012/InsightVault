from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from fraudlog.utils import record_failed_login

User = get_user_model()

@receiver(user_login_failed)
def handle_user_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get("username")
    if not username:
        return

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    if user:
        record_failed_login(user)
