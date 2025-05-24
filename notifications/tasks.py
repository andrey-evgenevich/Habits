from celery import shared_task
from django.utils import timezone
from habit.models import Habit
import requests
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_habit_notification(self, habit_id):
    try:
        habit = Habit.objects.select_related('user').get(pk=habit_id)

        if not habit.user.telegram_chat_id:
            return

        message = (
            f"⏰ Напоминание о привычке:\n"
            f"Действие: {habit.action}\n"
            f"Место: {habit.place}\n"
            f"Время: {habit.time.strftime('%H:%M')}\n"
            f"Длительность: {habit.duration} сек"
        )

        requests.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                'chat_id': habit.user.telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            },
            timeout=10
        )
    except Exception as exc:
        self.retry(exc=exc, countdown=60)


@shared_task
def check_due_habits():

    now = timezone.now()
    current_time = now.time()
    current_weekday = now.weekday()

    # Оптимизированный запрос с учетом периодичности
    habits = Habit.objects.filter(
        time__hour=current_time.hour,
        time__minute=current_time.minute,
        user__telegram_chat_id__isnull=False
    ).select_related('user')

    for habit in habits:
        # Проверка периодичности
        if habit.periodicity == 7:  # Weekly
            last_completed = habit.completions.order_by('-date').first()
            if last_completed and (now.date() - last_completed.date()).days < 7:
                continue

        send_habit_notification.delay(habit.id)