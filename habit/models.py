from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Habit(models.Model):
    class Periodicity(models.IntegerChoices):
        DAILY = 1, "Ежедневно"
        WEEKLY = 7, "Еженедельно"

    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="habits"
    )
    place = models.CharField(max_length=255, verbose_name="Место выполнения")
    time = models.TimeField(verbose_name="Время выполнения")
    action = models.CharField(max_length=255, verbose_name="Действие")
    is_pleasant = models.BooleanField(default=False, verbose_name="Приятная привычка")
    linked_habit = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    periodicity = models.PositiveSmallIntegerField(
        choices=Periodicity.choices,
        default=Periodicity.DAILY,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
    )
    reward = models.CharField(max_length=255, blank=True)
    duration = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        help_text="В секундах (макс. 120)",
    )
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_public"]),
            models.Index(fields=["time"]),
        ]
        ordering = ["time"]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.reward and self.linked_habit:
            raise ValidationError(
                "Нельзя указывать одновременно вознаграждение и связанную привычку"
            )
        if self.is_pleasant and (self.reward or self.linked_habit):
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки"
            )
        if self.linked_habit and not self.linked_habit.is_pleasant:
            raise ValidationError("Связанная привычка должна быть приятной")
