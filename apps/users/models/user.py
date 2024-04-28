from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    TYPE_CHOICES = (
        ('waitress', 'Ofisiant'),
        ('admin', 'Administrator'),
        ('restaurant', 'Restaurant Sahibi'),
    )

    type = models.CharField(
        choices=TYPE_CHOICES,
        max_length=32,
        blank=True,
        null=True,
    )
