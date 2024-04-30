from django.urls import path
from apps.meals.apis import MealCategoryAPIView
from apps.meals.apis import MealAPIView

urlpatterns = [
    path("categories/", MealCategoryAPIView.as_view()),
    path("meals/", MealAPIView.as_view()),
]
