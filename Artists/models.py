# Python imports
from django.db import models
# Django imports
import uuid


class Artist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'