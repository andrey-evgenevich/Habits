from django.db import models
from habit.models import Habit
from user.models import User
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SENT = "sent", _("Sent")
        FAILED = "failed", _("Failed")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("User"),
    )
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Habit"),
    )
    scheduled_time = models.DateTimeField(verbose_name=_("Scheduled Time"))
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Status"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-scheduled_time"]
        indexes = [
            models.Index(fields=["status", "scheduled_time"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"Notification for {self.habit} at {self.scheduled_time}"
