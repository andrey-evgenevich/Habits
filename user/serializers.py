from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'telegram_chat_id']
        read_only_fields = ['id']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class TelegramConnectionSerializer(serializers.Serializer):
    telegram_token = serializers.CharField(max_length=50)

    def validate_telegram_token(self, value):
        user = User.objects.filter(telegram_token=value).first()
        if not user:
            raise serializers.ValidationError("Invalid Telegram token")
        return user
