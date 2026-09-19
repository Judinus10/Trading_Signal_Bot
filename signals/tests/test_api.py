import pytest
from django.contrib.auth.models import User
from django.test import override_settings
@pytest.mark.django_db
@override_settings(SECURE_SSL_REDIRECT=False)
def test_health_requires_login(client):
    assert client.get("/api/v1/health/").status_code in (302,403)
@pytest.mark.django_db
@override_settings(SECURE_SSL_REDIRECT=False)
def test_health_for_owner(client):
    user=User.objects.create_user("owner",password="strong-test-password"); client.force_login(user); r=client.get("/api/v1/health/"); assert r.status_code==200; assert r.json()["status"]=="ok"
