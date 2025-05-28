import pytest
from rest_framework.test import APIRequestFactory
from habit.permissions import IsOwnerOrReadPublic
from habit.models import Habit
from user.models import User


@pytest.fixture
def factory():
    return APIRequestFactory()


@pytest.mark.django_db
class TestHabitPermissions:
    def test_owner_has_full_access(self, factory, user):
        habit = Habit.objects.create(
            user=user,
            place="Офис",
            time="10:00:00",
            action="Работа",
            duration=120
        )
        request = factory.get('/habits/')
        request.user = user
        permission = IsOwnerOrReadPublic()

        assert permission.has_object_permission(request, None, habit)

    def test_public_read_only(self, factory, user):
        other_user = User.objects.create_user(username='other')
        habit = Habit.objects.create(
            user=other_user,
            place="Парк",
            time="07:00:00",
            action="Бег",
            is_public=True,
            duration=30
        )
        request = factory.get('/habits/')
        request.user = user
        permission = IsOwnerOrReadPublic()

        assert permission.has_object_permission(request, None, habit)

        # Проверка, что нельзя изменять
        request = factory.patch('/habits/', {})
        request.user = user
        assert not permission.has_object_permission(request, None, habit)