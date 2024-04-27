from apps.meals.models import Meal
from apps.meals.models import MealCategory


from django.contrib import admin

admin.site.register(MealCategory)
admin.site.register(Meal)
