import pytest
from django.core.exceptions import ValidationError
from habit.models import Habit
from user.models import User
from datetime import time

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )

@pytest.fixture
def pleasant_habit(user):
    return Habit.objects.create(
        user=user,
        place="Дом",
        time=time(8, 0),
        action="Пить кофе",
        is_pleasant=True,
        duration=30
    )

@pytest.mark.django_db
class TestHabitModel:
    def test_create_habit(self, user):
        habit = Habit.objects.create(
            user=user,
            place="Парк",
            time=time(7, 0),
            action="Бег",
            duration=120
        )
        assert habit.pk is not None
        assert str(habit) == "Бег в 07:00:00 в Парк"

    def test_pleasant_habit_validation(self, user, pleasant_habit):
        # Нельзя добавить вознаграждение к приятной привычке
        habit = Habit(
            user=user,
            place="Дом",
            time=time(9, 0),
            action="Чтение",
            is_pleasant=True,
            reward="Конфета",
            duration=30
        )
        with pytest.raises(ValidationError):
            habit.full_clean()

    def test_linked_habit_must_be_pleasant(self, user, pleasant_habit):
        habit = Habit(
            user=user,
            place="Офис",
            time=time(12, 0),
            action="Работа",
            linked_habit=pleasant_habit,
            duration=60
        )
        habit.full_clean()  # Должно пройти валидацию

        # Создаем не приятную привычку
        non_pleasant = Habit.objects.create(
            user=user,
            place="Спортзал",
            time=time(18, 0),
            action="Тренировка",
            duration=90
        )
        habit.linked_habit = non_pleasant
        with pytest.raises(ValidationError):
            habit.full_clean()

    def test_duration_validation(self, user):
        habit = Habit(
            user=user,
            place="Дом",
            time=time(22, 0),
            action="Медитация",
            duration=121  # Превышает лимит
        )
        with pytest.raises(ValidationError):
            habit.full_clean()