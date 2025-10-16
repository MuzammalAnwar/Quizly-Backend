from django.contrib import admin
from django.urls import path
from .views import RegistrationView, CookieObtainPairView, CookieTokenRefreshView, LogoutView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name="register"),
    path('login/', CookieObtainPairView.as_view(), name="token_login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
]
