from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'habit', 'scheduled_time', 'status')
    list_filter = ('status', 'user')
    search_fields = ('user__username', 'habit__action')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'scheduled_time'