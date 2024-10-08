from django.db import models
from django.contrib.auth import get_user_model

from apps.commons.models import DateTimeModel

User = get_user_model()


class Room(DateTimeModel, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Zal"
        verbose_name_plural = "Zallar"

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

    class Meta:
        verbose_name = "Stol"
        verbose_name_plural = "Stollar"

    def __str__(self):
        return f"{self.number} | Ərazi {self.room.name if self.room else ''} "

    @property
    def waitress(self) -> User:
        order = self.current_order
        if order:
            return order.waitress
        return User.objects.none()

    @property
    def total_price(self):
        price = 0
        for order in self.orders:
            price += order.total_price
        return price

    @property
    def current_order(self):
        return self.orders.filter(is_paid=False, is_main=True).first()

    @property
    def assignable_table(self):
        return not self.orders.filter(is_paid=False).exists()

    def can_print_check(self):
        """
        Determines if the table has an active order 
        that hasn't had the check printed yet.

        Returns:
            can_print (bool): True if there is an active, 
            unpaid order with an unprinted check, False otherwise.
        """
        active_order = self.current_order
        return (
            active_order is not None and
            not active_order.is_check_printed and
            not active_order.is_paid
        )
