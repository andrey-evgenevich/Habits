from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from habit.views import HabitViewSet, PublicListView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(router.urls)),
    path('api/users/', include('user.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/habits/public/', HabitViewSet.as_view({'get': 'list'}), name='public-habits'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('public-habits/', PublicListView.as_view(), name='public-habits'),
]
