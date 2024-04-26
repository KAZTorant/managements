
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, pin, password, **extra_fields):
        """Create and save a User with the given pin and password."""
        if not pin:
            raise ValueError('The given pin must be set')

        user = self.model(pin=pin, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, pin, password=None, **extra_fields):
        """Create and save a regular User with the given pin and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(pin, password, **extra_fields)

    def create_superuser(self, pin, password, **extra_fields):
        """Create and save a SuperUser with the given pin and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(pin, password, **extra_fields)


class User(AbstractUser):

    username = None
    pin = models.CharField(max_length=16, unique=True)

    USERNAME_FIELD = "pin"
    REQUIRED_FIELDS = []

    objects = UserManager()
