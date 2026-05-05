import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@pytest.mark.django_db
def test_analytics_endpoint():
    user = User.objects.create_user(username="testuser", password="pass123")
    user.role = "analyst"
    user.save()

    refresh = RefreshToken.for_user(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    url = reverse("transaction-summary")
    response = client.get(url)

    assert response.status_code == 200
