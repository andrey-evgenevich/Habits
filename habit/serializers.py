from rest_framework import serializers
from .models import Habit
from .validators import validate_habit_consistency

class HabitSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if hasattr(instance.time, 'strftime'):
            representation['time'] = instance.time.strftime('%H:%M')
        else:
            representation['time'] = str(instance.time)
        return representation

    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
        extra_kwargs = {
            'duration': {'help_text': 'Время выполнения в секундах (максимум 120)'}
        }

    def validate(self, data):
        habit = Habit(**data)
        validate_habit_consistency(habit)
        return data