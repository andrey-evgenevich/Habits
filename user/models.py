from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    telegram_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Telegram Chat ID"),
        help_text=_("ID чата в Telegram для отправки уведомлений"),
    )
    telegram_token = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("Telegram Token"),
        help_text=_("Токен для подключения Telegram бота"),
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["username"]

    def __str__(self):
        return self.username

    def generate_telegram_token(self):
        import secrets

        self.telegram_token = secrets.token_urlsafe(16)
        self.save()
        return self.telegram_token
