from django.contrib import admin

from .models import Board
from tasks_app.models import Task


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1 
    fields = ('title', 'status', 'priority', 'assignee', 'reviewer', 'due_date')
    show_change_link = True


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner')
    search_fields = ('title', 'owner__email')
    list_filter = ('owner',)

    inlines = [TaskInline]