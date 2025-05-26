from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'telegram_chat_id', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }
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
