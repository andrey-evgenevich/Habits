# from rest_framework import status
# from rest_framework.test import APIClient
# from datetime import time
# from rest_framework.test import APIRequestFactory
# from habit.permissions import IsOwnerOrReadPublic
# import pytest
# from django.core.exceptions import ValidationError
# from habit.validators import validate_habit_consistency
# from habit.models import Habit
# from user.models import User
#
#
# @pytest.mark.django_db
# class TestHabitValidators:
#     def test_reward_and_linked_habit_validation(self, user):
#         habit = Habit(
#             user=user,
#             place="Дом",
#             time="09:00:00",
#             action="Работа",
#             reward="Кофе",
#             linked_habit_id=1,
#             duration=60,
#         )
#         with pytest.raises(ValidationError) as exc:
#             validate_habit_consistency(habit)
#         assert "Выберите что-то одно" in str(exc.value)
#
#     def test_pleasant_habit_with_reward(self, user):
#         habit = Habit(
#             user=user,
#             place="Диван",
#             time="20:00:00",
#             action="Отдых",
#             is_pleasant=True,
#             reward="Чай",
#             duration=30,
#         )
#         with pytest.raises(ValidationError) as exc:
#             validate_habit_consistency(habit)
#         assert "У приятной привычки не может быть вознаграждения" in str(exc.value)
#
#     def test_valid_habit(self, user):
#         habit = Habit(
#             user=user,
#             place="Спортзал",
#             time="19:00:00",
#             action="Тренировка",
#             duration=90,
#         )
#         validate_habit_consistency(habit)  # Не должно быть исключений
#
#
# @pytest.fixture
# def factory():
#     return APIRequestFactory()
#
#
# @pytest.mark.django_db
# class TestHabitPermissions:
#     def test_owner_has_full_access(self, factory, user):
#         habit = Habit.objects.create(
#             user=user, place="Офис", time="10:00:00", action="Работа", duration=120
#         )
#         request = factory.get("/habits/")
#         request.user = user
#         permission = IsOwnerOrReadPublic()
#
#         assert permission.has_object_permission(request, None, habit)
#
#     def test_public_read_only(self, factory, user):
#         other_user = User.objects.create_user(username="other")
#         habit = Habit.objects.create(
#             user=other_user,
#             place="Парк",
#             time="07:00:00",
#             action="Бег",
#             is_public=True,
#             duration=30,
#         )
#         request = factory.get("/habits/")
#         request.user = user
#         permission = IsOwnerOrReadPublic()
#
#         assert permission.has_object_permission(request, None, habit)
#
#         # Проверка, что нельзя изменять
#         request = factory.patch("/habits/", {})
#         request.user = user
#         assert not permission.has_object_permission(request, None, habit)
#
#
# @pytest.fixture
# def user():
#     return User.objects.create_user(
#         username="testuser", password="testpass123", email="test@example.com"
#     )
#
#
# @pytest.fixture
# def pleasant_habit(user):
#     return Habit.objects.create(
#         user=user,
#         place="Дом",
#         time=time(8, 0),
#         action="Пить кофе",
#         is_pleasant=True,
#         duration=30,
#     )
#
#
# @pytest.mark.django_db
# class TestHabitModel:
#     def test_create_habit(self, user):
#         habit = Habit.objects.create(
#             user=user, place="Парк", time=time(7, 0), action="Бег", duration=120
#         )
#         assert habit.pk is not None
#         assert str(habit) == "Бег в 07:00:00 в Парк"
#
#     def test_pleasant_habit_validation(self, user, pleasant_habit):
#         # Нельзя добавить вознаграждение к приятной привычке
#         habit = Habit(
#             user=user,
#             place="Дом",
#             time=time(9, 0),
#             action="Чтение",
#             is_pleasant=True,
#             reward="Конфета",
#             duration=30,
#         )
#         with pytest.raises(ValidationError):
#             habit.full_clean()
#
#     def test_linked_habit_must_be_pleasant(self, user, pleasant_habit):
#         habit = Habit(
#             user=user,
#             place="Офис",
#             time=time(12, 0),
#             action="Работа",
#             linked_habit=pleasant_habit,
#             duration=60,
#         )
#         habit.full_clean()  # Должно пройти валидацию
#
#         # Создаем не приятную привычку
#         non_pleasant = Habit.objects.create(
#             user=user,
#             place="Спортзал",
#             time=time(18, 0),
#             action="Тренировка",
#             duration=90,
#         )
#         habit.linked_habit = non_pleasant
#         with pytest.raises(ValidationError):
#             habit.full_clean()
#
#     def test_duration_validation(self, user):
#         habit = Habit(
#             user=user,
#             place="Дом",
#             time=time(22, 0),
#             action="Медитация",
#             duration=121,  # Превышает лимит
#         )
#         with pytest.raises(ValidationError):
#             habit.full_clean()
#
#
# @pytest.fixture
# def api_client():
#     return APIClient()
#
#
# @pytest.fixture
# def auth_client(user, api_client):
#     api_client.force_authenticate(user=user)
#     return api_client
#
#
# @pytest.mark.django_db
# class TestHabitAPI:
#     def test_create_habit_authenticated(self, auth_client):
#         payload = {
#             "place": "Парк",
#             "time": "07:00:00",
#             "action": "Утренний бег",
#             "duration": 60,
#         }
#         response = auth_client.post("/api/habits/", payload)
#         assert response.status_code == status.HTTP_201_CREATED
#         assert Habit.objects.count() == 1
#
#     def test_create_habit_unauthenticated(self, api_client):
#         response = api_client.post("/api/habits/", {})
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
#
#     def test_get_public_habits(self, api_client, user):
#         Habit.objects.create(
#             user=user,
#             place="Библиотека",
#             time="15:00:00",
#             action="Чтение",
#             is_public=True,
#             duration=30,
#         )
#         response = api_client.get("/api/habits/public/")
#         assert response.status_code == status.HTTP_200_OK
#         assert len(response.data["results"]) == 1
#
#     def test_update_habit_owner(self, auth_client, user):
#         habit = Habit.objects.create(
#             user=user, place="Дом", time="08:00:00", action="Зарядка", duration=15
#         )
#         response = auth_client.patch(
#             f"/api/habits/{habit.id}/", {"action": "Утренняя зарядка"}
#         )
#         assert response.status_code == status.HTTP_200_OK
#         habit.refresh_from_db()
#         assert habit.action == "Утренняя зарядка"
#
#     def test_update_habit_non_owner(self, auth_client, user):
#         other_user = User.objects.create_user(username="other", password="otherpass")
#         habit = Habit.objects.create(
#             user=other_user, place="Кафе", time="12:00:00", action="Обед", duration=30
#         )
#         response = auth_client.patch(
#             f"/api/habits/{habit.id}/", {"action": "Измененное действие"}
#         )
#         assert response.status_code == status.HTTP_403_FORBIDDEN
