from django.test import TestCase
from django.utils import timezone
from notifications.models import Notification
from habit.models import Habit
from user.models import User


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