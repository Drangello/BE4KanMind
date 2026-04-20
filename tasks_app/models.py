from django.db import models
from django.conf import settings
from boards_app.models import Board

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='to-do')
    priority = models.CharField(max_length=50, default='medium')
    due_date = models.DateField(null=True, blank=True)
    board = models.ForeignKey(Board, related_name='tasks', on_delete=models.CASCADE)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviewed_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tasks', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
