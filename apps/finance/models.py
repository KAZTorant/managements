from django.db import models
from django.utils.timezone import now


class Income(models.Model):
    PAYMENT_TYPES = [
        ('cashier', 'Cashier'),
        ('c2c', 'C2C'),
        ('nfs', 'NFS'),
    ]
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES)
    description = models.TextField(
        blank=True, null=True)  # Optional description
    date = models.DateField(default=now)

    class Meta:
        verbose_name = "Gəlir"
        verbose_name_plural = "Gəlirlər"

    def __str__(self):
        return f"{self.payment_type} - {self.amount}"


class Expense(models.Model):
    CATEGORY_TYPES = [
        ('salary', 'Salary'),
        ('fees', 'Fees'),
        ('other', 'Other'),
    ]
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    description = models.TextField(
        blank=True, null=True)  # Optional description
    date = models.DateField(default=now)

    class Meta:
        verbose_name = "Xərc"
        verbose_name_plural = "Xərclər"

    def __str__(self):
        return f"{self.category} - {self.amount}"
