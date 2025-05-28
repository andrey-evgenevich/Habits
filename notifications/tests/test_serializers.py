from rest_framework.test import APITestCase
from rest_framework import serializers
from notifications.serializers import NotificationSerializer
from notifications.models import Notification
from habit.models import Habit
from user.models import User
from django.utils import timezone


class NotificationSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time="08:00:00",
            action="Зарядка",
            duration=30
        )
        self.notification = Notification.objects.create(
            user=self.user,
            habit=self.habit,
            scheduled_time=timezone.now()
        )

    def test_serializer_fields(self):
        serializer = NotificationSerializer(instance=self.notification)
        data = serializer.data
        self.assertEqual(set(data.keys()), {
            'id', 'habit', 'scheduled_time', 'status',
            'created_at', 'updated_at', 'error_message'
        })

    def test_read_only_fields(self):
        initial_data = {
            'habit': {'id': self.habit.id},
            'status': 'sent',
            'scheduled_time': timezone.now().isoformat()
        }
        serializer = NotificationSerializer(data=initial_data)
        self.assertTrue(serializer.is_valid())

        # Попытка изменить read-only поле
        data = serializer.validated_data
        data['status'] = 'failed'
        notification = serializer.save(user=self.user)
        self.assertEqual(notification.status, 'pending')  # Значение по умолчанию