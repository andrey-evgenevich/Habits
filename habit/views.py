from django.shortcuts import render

from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwnerOrReadPublic
from .pagination import HabitPagination


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadPublic]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_pleasant', 'is_public']
    ordering_fields = ['time', 'created_at']
    ordering = ['time']

    def get_queryset(self):
        queryset = Habit.objects.select_related('user', 'linked_habit')

        if self.action == 'public':
            return queryset.filter(is_public=True)

        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
