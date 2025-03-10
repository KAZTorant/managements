from django.urls import path
from apps.finance.views import IncomeCreateView, ExpenseCreateView, DailyResultView, IncomeListView, ExpenseListView, AllResultsView

urlpatterns = [
    path('income/', IncomeCreateView.as_view(), name='add_income'),
    path('expense/', ExpenseCreateView.as_view(), name='add_expense'),
    path('incomes/', IncomeListView.as_view(), name='list_incomes'),
    path('expenses/', ExpenseListView.as_view(), name='list_expenses'),
    path('daily-result/', DailyResultView.as_view(), name='daily_result'),
    path('all-results/', AllResultsView.as_view(), name='all_results'),
]