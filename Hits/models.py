# Python imports
import uuid
# Django imports
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
# Internal imports
from Artists.models import Artist


class Hit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, validators=[MinLengthValidator(2), MaxLengthValidator(255)])
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['created_at']),
            models.Index(fields=['artist']),
        ]

    def __str__(self):
        return self.title
