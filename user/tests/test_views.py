from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from user.models import User
import json


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