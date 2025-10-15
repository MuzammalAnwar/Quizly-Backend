from django.contrib import admin
from django.urls import path
from .views import RegistrationView, CookieObtainPairView, CookieTokenRefreshView, LogoutView

urlpatterns = [
    path('register/', RegistrationView.as_view()),
    path('login/', CookieObtainPairView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
]
