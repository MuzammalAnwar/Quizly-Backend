from django.contrib import admin
from django.urls import path
from .views import RegistrationView, CookieObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view()),
    path('login/', CookieObtainPairView.as_view()),
    # path('logout/', admin.site.urls),
    # path('token/refresh/', admin.site.urls),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
