from django.test import TestCase
from django.core.exceptions import ValidationError
from user.models import User
import secrets


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_telegram_token_generation(self):
        user = User.objects.create_user(
            username='telegramuser',
            password='testpass'
        )
        token = user.generate_telegram_token()
        self.assertEqual(len(token), 22)  # Длина токена secrets.token_urlsafe(16)
        self.assertEqual(user.telegram_token, token)

    def test_telegram_token_uniqueness(self):
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')

        token1 = user1.generate_telegram_token()
        token2 = user2.generate_telegram_token()

        self.assertNotEqual(token1, token2)