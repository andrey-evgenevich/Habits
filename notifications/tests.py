from rest_framework.test import APITestCase
from notifications.serializers import NotificationSerializer
from unittest.mock import patch
from notifications.tasks import send_habit_notification, check_due_habits
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from notifications.models import Notification
from habit.models import Habit
from user.models import User
from django.utils import timezone


    # models
class NotificationModelTest(TestCase):
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

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user,
            habit=self.habit,
            scheduled_time=timezone.now()
        )
        self.assertEqual(notification.status, 'pending')
        self.assertIsNone(notification.error_message)
        self.assertEqual(str(notification),
                         f"Notification for {self.habit} at {notification.scheduled_time}")

    def test_status_choices(self):
        notification = Notification.objects.create(
            user=self.user,
            habit=self.habit,
            scheduled_time=timezone.now()
        )
        self.assertIn(notification.status, [choice[0] for choice in Notification.Status.choices])

    def test_default_ordering(self):
        now = timezone.now()
        Notification.objects.create(
            user=self.user,
            habit=self.habit,
            scheduled_time=now - timezone.timedelta(days=1)
        )
        Notification.objects.create(
            user=self.user,
            habit=self.habit,
            scheduled_time=now + timezone.timedelta(days=1)
        )

        notifications = Notification.objects.all()
        self.assertGreater(notifications[0].scheduled_time, notifications[1].scheduled_time)


    # serializers
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


    # tasks
class NotificationTasksTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            telegram_chat_id='12345'
        )
        self.habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time="08:00:00",
            action="Зарядка",
            duration=30
        )

    @patch('notifications.tasks.requests.post')
    def test_send_habit_notification_success(self, mock_post):
        mock_post.return_value.status_code = 200
        send_habit_notification(self.habit.id)
        mock_post.assert_called_once()
        self.assertIn('Зарядка', mock_post.call_args[1]['json']['text'])

    @patch('notifications.tasks.requests.post')
    def test_send_habit_notification_no_telegram(self, mock_post):
        self.user.telegram_chat_id = None
        self.user.save()
        send_habit_notification(self.habit.id)
        mock_post.assert_not_called()

    @patch('notifications.tasks.requests.post')
    def test_send_habit_notification_retry_on_failure(self, mock_post):
        mock_post.side_effect = Exception('Test error')
        with self.assertRaises(Exception):
            send_habit_notification(self.habit.id, countdown=1)
        self.assertEqual(mock_post.call_count, 3)

    @patch('notifications.tasks.send_habit_notification.delay')
    def test_check_due_habits(self, mock_send):
        now = timezone.now()
        habit_time = now.time().replace(second=0, microsecond=0)
        self.habit.time = habit_time
        self.habit.save()

        check_due_habits()
        mock_send.assert_called_once_with(self.habit.id)


    # views
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
