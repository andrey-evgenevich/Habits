from rest_framework import serializers
from .models import Notification
from habits.serializers import HabitSerializer


class NotificationSerializer(serializers.ModelSerializer):
    habit = HabitSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'habit',
            'scheduled_time',
            'status',
            'created_at',
            'updated_at',
            'error_message'
        ]
        read_only_fields = fields
