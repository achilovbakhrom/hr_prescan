from django.contrib import admin

from apps.notifications.models import Message, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "title", "is_read", "created_at")
    list_filter = ("type", "is_read", "created_at")
    search_fields = ("title", "message", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "application", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("content", "sender__email", "recipient__email")
    readonly_fields = ("id", "created_at", "updated_at")
