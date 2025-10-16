import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

pytestmark = pytest.mark.django_db


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def registration_payload():
    return {
        "username": "Testuser",
        "email": "test@test.com",
        "password": "Test1234",
        "confirmed_password": "Test1234",
    }


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username="test", email="test@example.com", password="Test1234"
    )


def test_registration_success(api, registration_payload):
    url = reverse("register")
    res = api.post(url, registration_payload, format="json")
    assert res.status_code == status.HTTP_200_OK
    assert res.data == {"detail": "User created successfully!"}


def test_registration_validation_error(api):
    url = reverse("register")
    res = api.post(url, {"username": ""}, format="json")
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(res.data, dict) and res.data


def test_login_success(api, user):
    url = reverse("token_login")
    res = api.post(
        url, {"username": "test", "password": "Test1234"}, format="json")
    assert res.status_code == status.HTTP_200_OK
    assert res.data["detail"] == "Login successful!"
    assert res.data["user"]["id"] == user.id
    assert res.data["user"]["username"] == "test"
    assert res.data["user"]["email"] == "test@example.com"


def test_refresh_without_cookie_returns_401(api):
    url = reverse("token_refresh")
    res = api.post(url, {}, format="json")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert res.data["detail"] == "Refresh Token not found!"


def test_refresh_with_cookie_success(api, user):
    login_url = reverse("token_login")
    login_res = api.post(
        login_url, {"username": "test", "password": "Test1234"}, format="json")
    assert login_res.status_code == status.HTTP_200_OK

    api.cookies["refresh_token"] = login_res.cookies["refresh_token"].value

    refresh_url = reverse("token_refresh")
    res = api.post(refresh_url, {}, format="json")
    assert res.status_code == status.HTTP_200_OK
    assert res.data["detail"] == "Token refreshed"
    assert "access" in res.data and res.data["access"]


def test_logout_requires_auth_and_works(api, user):
    url = reverse("logout")

    # Unauthenticated -> 401/403
    res_unauth = api.post(url)
    assert res_unauth.status_code in (
        status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    token = str(AccessToken.for_user(user))
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    res = api.post(url)
    assert res.status_code == status.HTTP_200_OK
    assert "Log-Out successfully!" in res.data["detail"]
