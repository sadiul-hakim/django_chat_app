from django.contrib import admin
from .models import Room, Message
# Register your models here.


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)
    search_fields = ('name', 'slug',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'room', 'user', 'created_at',)
    search_fields = ('content', 'room', 'user',)
