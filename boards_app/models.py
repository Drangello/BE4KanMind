from django.conf import settings
from django.db import models

class Board(models.Model):
    """
    Board model representing a Kanban board.

    Attributes:
        title (CharField): The name of the board.
        created_at (DateTimeField): The timestamp when the board was created.
        owner (ForeignKey): The User who created and owns the board.
        members (ManyToManyField): Users who have access to view and interact with the board.
    """
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_boards'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='boards',
        blank=True
    )

    def __str__(self):
        return self.title
