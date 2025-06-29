from django.core.exceptions import ValidationError


def validate_habit_consistency(habit):
    """Комплексная валидация привычки"""
    errors = {}

    if habit.duration > 120:
        errors["duration"] = "Время выполнения не может превышать 120 секунд"

    if habit.reward and habit.linked_habit:
        errors["reward"] = errors["linked_habit"] = (
            "Выберите что-то одно: вознаграждение или связанную привычку"
        )

    if errors:
        raise ValidationError(errors)
