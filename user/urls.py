from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserCreateView,
    UserDetailView,
    CustomTokenObtainPairView,
    TelegramConnectView,
    GenerateTelegramTokenView
)

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('telegram/connect/', TelegramConnectView.as_view(), name='telegram-connect'),
    path('telegram/token/', GenerateTelegramTokenView.as_view(), name='generate-telegram-token'),
]
