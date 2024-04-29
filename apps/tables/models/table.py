from django.db import models
from django.contrib.auth import get_user_model

from apps.commons.models import DateTimeModel

User = get_user_model()


class Room(DateTimeModel, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Table(DateTimeModel, models.Model):
    number = models.CharField(max_length=10, blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    room = models.ForeignKey(
        Room,
        related_name='tables',
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"{self.number} | Ərazi {self.room.name} "

    @property
    def waitress(self) -> User:
        order = self.orders.filter(is_paid=False).first()
        if order:
            return order.waitress
        return User.objects.none()

    @property
    def total_price(self):
        order = self.orders.filter(is_paid=False).first()
        if order:
            return order.total_price
        return 0
