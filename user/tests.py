from rest_framework.test import APITestCase
from user.serializers import UserSerializer, TelegramConnectionSerializer
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from user.models import User

#     models
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


    # serializers
class UserSerializerTest(APITestCase):
    def test_create_user_with_serializer(self):
        data = {
            'username': 'serializeruser',
            'email': 'serializer@example.com',
            'password': 'complexpass123',
            'telegram_chat_id': '12345'
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(user.username, 'serializeruser')
        self.assertTrue(check_password('complexpass123', user.password))
        self.assertEqual(user.telegram_chat_id, '12345')

    def test_password_write_only(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        serializer = UserSerializer(user)
        self.assertNotIn('password', serializer.data)


class TelegramConnectionSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='telegramuser',
            password='testpass'
        )
        self.token = self.user.generate_telegram_token()

    def test_valid_token(self):
        serializer = TelegramConnectionSerializer(data={'telegram_token': self.token})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, self.user)

    def test_invalid_token(self):
        serializer = TelegramConnectionSerializer(data={'telegram_token': 'invalid'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('telegram_token', serializer.errors)


    # views
class UserViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )

    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_jwt_authentication(self):
        response = self.client.post('/api/users/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_get_current_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_generate_telegram_token(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/users/telegram/token/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('telegram_token', response.data)
        self.user.refresh_from_db()
        self.assertEqual(response.data['telegram_token'], self.user.telegram_token)

    def test_telegram_connection(self):
        self.client.force_authenticate(user=self.user)
        token = self.user.generate_telegram_token()

        response = self.client.post('/api/users/telegram/connect/', {
            'telegram_token': token,
            'chat_id': '12345'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.telegram_chat_id, '12345')