from django.db import models


# Model for Meal Category
class MealCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Model for Meal
class Meal(models.Model):
    category = models.ForeignKey(
        MealCategory,
        related_name='meals',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name