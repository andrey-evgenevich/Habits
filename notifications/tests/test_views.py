from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from notifications.models import Notification
from habit.models import Habit
from user.models import User
from django.utils import timezone

class NotificationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
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
        self.client.force_authenticate(user=self.user)

    def test_list_notifications_authenticated(self):
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_notifications_unauthenticated(self):
        client = APIClient()
        response = client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_status(self):
        Notification.objects.create(
            user=self.user,
            habit=self.habit,
            scheduled_time=timezone.now(),
            status='sent'
        )
        response = self.client.get('/api/notifications/?status=sent')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'sent')

    def test_user_sees_only_own_notifications(self):
        Notification.objects.create(
            user=self.other_user,
            habit=self.habit,
            scheduled_time=timezone.now()
        )
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)