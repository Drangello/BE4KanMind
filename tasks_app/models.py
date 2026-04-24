from django.conf import settings
from django.db import models

from boards_app.models import Board

class Task(models.Model):
    """
    Task model representing an actionable item on a Kanban Board.
    
    Attributes:
        title (CharField): Title of the task.
        description (TextField): Detailed description.
        status (CharField): Flow state (to-do, in-progress, review, done).
        priority (CharField): Importance (low, medium, high).
        due_date (DateField): Deadline for the task.
        board (ForeignKey): The Board this task belongs to.
        assignee (ForeignKey): User assigned to work on the task.
        reviewer (ForeignKey): User assigned to review the task.
        creator (ForeignKey): User who created the task.
    """
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

class Comment(models.Model):
    """
    Comment model for discussion on Tasks.
    
    Attributes:
        task (ForeignKey): The Task being commented on.
        author (ForeignKey): The User who wrote the comment.
        content (TextField): The body of the comment.
        created_at (DateTimeField): When the comment was created.
    """
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.fullname} on {self.task.title}"
