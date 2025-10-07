from django.contrib import admin
from .models import chat_telegram
# Register your models here.

@admin.register(chat_telegram)
class chat_telegramAdmin(admin.ModelAdmin):
      list_display = ("id", "user", "text", "created_at")