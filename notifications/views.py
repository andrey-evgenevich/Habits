from rest_framework import generics, permissions
from .models import Notification
from .serializers import NotificationSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['scheduled_time', 'created_at']
    ordering = ['-scheduled_time']

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).select_related('habit', 'user')
