from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from apps.commons.models import DateTimeModel
from apps.meals.models import Meal
from apps.tables.models import Table
from django.db.models import Sum
from django.utils import timezone
from simple_history.models import HistoricalRecords


User = get_user_model()

# Model for Order


class Order(DateTimeModel, models.Model):
    table = models.ForeignKey(
        Table,
        related_name='orders',
        on_delete=models.CASCADE,
        verbose_name="Stol"
    )
    meals = models.ManyToManyField(
        Meal, through='OrderItem', verbose_name="Yemək")
    is_paid = models.BooleanField(default=False, verbose_name="Ödənilib")
    is_check_printed = models.BooleanField(
        default=False, verbose_name="Çek çıxarılıb")
    waitress = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        blank=True,
        null=True,
        verbose_name="Ofisiant"
    )
    total_price = models.DecimalField(
        default=0, max_digits=10, decimal_places=2,
        verbose_name="Ümumi"
    )
    history = HistoricalRecords()

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


class OrderItem(DateTimeModel, models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name="Sifariş"
    )
    meal = models.ForeignKey(
        Meal, on_delete=models.CASCADE, verbose_name="Yemək")
    quantity = models.IntegerField(default=1, verbose_name="Miqdar")
    is_prepared = models.BooleanField(
        default=False
    )
    # Adjusted for total price
    price = models.DecimalField(
        max_digits=9, decimal_places=2, default=0.00, verbose_name="Məbləğ")
    is_deleted_by_adminstrator = models.BooleanField(default=False)
    item_added_at = models.DateTimeField(
        default=timezone.now, blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Sifariş məhsulu"
        verbose_name_plural = "Sifariş məhsulları"

    def __str__(self):
        try:
            return f"{self.quantity} x {self.meal.name} | Qiymət: {self.quantity*self.meal.price}"
        except:
            return "Yemek Yoxdur"
