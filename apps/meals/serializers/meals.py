from rest_framework import serializers

from apps.meals.models import Meal
from apps.meals.models import MealCategory


class MealCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MealCategory
        fields = (
            "id",
            "name",
            "description",
        )


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = (
            "id",
            "name",
            "description",
            "price"
        )
