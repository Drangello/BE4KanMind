from django.contrib import admin
from .models import Task, Comment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'board', 'status', 'priority', 'assignee', 'reviewer')
    list_filter = ('status', 'priority', 'board')
    search_fields = ('title', 'description')
    autocomplete_fields = ('assignee', 'reviewer', 'board')


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('author', 'content', 'created_at')
    readonly_fields = ('author', 'created_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'author', 'created_at')
    search_fields = ('content', 'author__fullname')