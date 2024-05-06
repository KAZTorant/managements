from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from apps.meals.models import Meal
from apps.tables.models import Table
from django.db.models import F, Sum


User = get_user_model()

# Model for Order


class Order(models.Model):
    table = models.ForeignKey(
        Table,
        related_name='orders',
        on_delete=models.CASCADE
    )
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
    total_price = models.DecimalField(
        default=0, max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Sifariş"
        verbose_name_plural = "Sifarişlər"

    def __str__(self):
        return f"Order {self.id} for {self.table}"

    def update_total_price(self):
        total_price = self.order_items.aggregate(
            total=Sum('price', output_field=models.DecimalField())
        )['total'] or Decimal(0)
        self.total_price = total_price
        self.save()

# Intermediate model for Order and Meal relationship


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items"
    )
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    is_prepared = models.BooleanField(
        default=False
    )
    # Adjusted for total price
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Sifariş məhsulu"
        verbose_name_plural = "Sifariş məhsulları"

    def __str__(self):
        try:
            return f"{self.quantity} x {self.meal.name} | Qiymət: {self.quantity*self.meal.price}"
        except:
            return "Yemek Yoxdur"
