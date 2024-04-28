from django.db import models
from django.contrib.auth import get_user_model
from apps.meals.models import Meal
from apps.tables.models import Table

User = get_user_model()

# Model for Order


class Order(models.Model):
    table = models.ForeignKey(
        Table, related_name='orders', on_delete=models.CASCADE)
    meals = models.ManyToManyField(Meal, through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    is_check_printed = models.BooleanField(default=False)
    waitress = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Order {self.id} for {self.table}"


# Intermediate model for Order and Meal relationship
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    is_prepared = models.BooleanField(
        default=False)  # To track preparation status

    def __str__(self):
        return f"{self.quantity} x {self.meal.name} | Qiymət: {self.quantity*self.meal.price}"
