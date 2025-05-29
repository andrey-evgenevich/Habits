from rest_framework.test import APITestCase
from rest_framework import serializers
from user.serializers import UserSerializer, TelegramConnectionSerializer
from user.models import User
from django.contrib.auth.hashers import check_password


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