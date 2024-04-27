
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True


class User(AbstractUser):

    pin = models.CharField(max_length=16, unique=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()
