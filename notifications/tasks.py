from celery import shared_task
from django.utils import timezone
from habit.models import Habit
import requests
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_habit_notification(self, habit_id, countdown=1):
    try:
        habit = Habit.objects.get(pk=habit_id)
        if not habit.user.telegram_chat_id:
            return
        message = (
            f"⏰ Напоминание о привычке:\n"
            f"Действие: {habit.action}\n"
            f"Место: {habit.place}\n"
            f"Время: {habit.time}\n"
            f"Длительность: {habit.duration} сек"
        )
        response = requests.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": habit.user.telegram_chat_id, "text": message},
            timeout=10,
        )
        response.raise_for_status()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=countdown)


@shared_task
def check_due_habits():

    now = timezone.now()
    current_time = now.time()

    habits = Habit.objects.filter(
        time__hour=current_time.hour,
        time__minute=current_time.minute,
        user__telegram_chat_id__isnull=False,
    ).select_related("user")

    for habit in habits:
        # Проверка периодичности
        if habit.periodicity == 7:  # Weekly
            last_completed = habit.completions.order_by("-date").first()
            if last_completed and (now.date() - last_completed.date()).days < 7:
                continue

        send_habit_notification.delay(habit.id)
