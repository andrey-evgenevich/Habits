import pytest
from rest_framework import status
from rest_framework.test import APIClient
from habit.models import Habit
from user.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client(user, api_client):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
class TestHabitAPI:
    def test_create_habit_authenticated(self, auth_client):
        payload = {
            "place": "Парк",
            "time": "07:00:00",
            "action": "Утренний бег",
            "duration": 60
        }
        response = auth_client.post('/api/habits/', payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert Habit.objects.count() == 1

    def test_create_habit_unauthenticated(self, api_client):
        response = api_client.post('/api/habits/', {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_public_habits(self, api_client, user):
        Habit.objects.create(
            user=user,
            place="Библиотека",
            time="15:00:00",
            action="Чтение",
            is_public=True,
            duration=30
        )
        response = api_client.get('/api/habits/public/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_update_habit_owner(self, auth_client, user):
        habit = Habit.objects.create(
            user=user,
            place="Дом",
            time="08:00:00",
            action="Зарядка",
            duration=15
        )
        response = auth_client.patch(
            f'/api/habits/{habit.id}/',
            {'action': 'Утренняя зарядка'}
        )
        assert response.status_code == status.HTTP_200_OK
        habit.refresh_from_db()
        assert habit.action == "Утренняя зарядка"

    def test_update_habit_non_owner(self, auth_client, user):
        other_user = User.objects.create_user(
            username='other',
            password='otherpass'
        )
        habit = Habit.objects.create(
            user=other_user,
            place="Кафе",
            time="12:00:00",
            action="Обед",
            duration=30
        )
        response = auth_client.patch(
            f'/api/habits/{habit.id}/',
            {'action': 'Измененное действие'}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN