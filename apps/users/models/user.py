from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    TYPE_CHOICES = (
        ('waitress', 'Ofisiant'),
        ('captain_waitress', 'Kapitan Ofisiant'),
        ('admin', 'Administrator'),
        ('restaurant', 'Restaurant Sahibi'),
    )

    type = models.CharField(
        choices=TYPE_CHOICES,
        max_length=32,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.get_full_name() or self.username}"
