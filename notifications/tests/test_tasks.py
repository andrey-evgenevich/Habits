from django.test import TestCase
from unittest.mock import patch
from notifications.tasks import send_habit_notification, check_due_habits
from habit.models import Habit
from user.models import User
from django.utils import timezone


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