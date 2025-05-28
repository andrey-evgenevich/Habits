import pytest
from django.core.exceptions import ValidationError
from habit.validators import validate_habit_consistency
from habit.models import Habit
from user.models import User

@pytest.mark.django_db
class TestHabitValidators:
    def test_reward_and_linked_habit_validation(self, user):
        habit = Habit(
            user=user,
            place="Дом",
            time="09:00:00",
            action="Работа",
            reward="Кофе",
            linked_habit_id=1,
            duration=60
        )
        with pytest.raises(ValidationError) as exc:
            validate_habit_consistency(habit)
        assert "Выберите что-то одно" in str(exc.value)

    def test_pleasant_habit_with_reward(self, user):
        habit = Habit(
            user=user,
            place="Диван",
            time="20:00:00",
            action="Отдых",
            is_pleasant=True,
            reward="Чай",
            duration=30
        )
        with pytest.raises(ValidationError) as exc:
            validate_habit_consistency(habit)
        assert "У приятной привычки не может быть вознаграждения" in str(exc.value)

    def test_valid_habit(self, user):
        habit = Habit(
            user=user,
            place="Спортзал",
            time="19:00:00",
            action="Тренировка",
            duration=90
        )
        validate_habit_consistency(habit)  # Не должно быть исключений