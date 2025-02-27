from django.urls import path
from .views import IncomeCreateView, ExpenseCreateView, DailyResultView

urlpatterns = [
    path('income/', IncomeCreateView.as_view(), name='add_income'),
    path('expense/', ExpenseCreateView.as_view(), name='add_expense'),
    path('daily-result/', DailyResultView.as_view(), name='daily_result'),
]
