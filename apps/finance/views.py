from rest_framework import generics
from django.db.models import Sum
from rest_framework.response import Response
from datetime import date

from .models import Income, Expense
from .serializers import IncomeSerializer, ExpenseSerializer

class IncomeCreateView(generics.CreateAPIView):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class ExpenseCreateView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class DailyResultView(generics.GenericAPIView):
    def get(self, request):
        today = date.today()
        total_income = Income.objects.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = Expense.objects.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or 0
        result = total_income - total_expense
        return Response({"date": today, "total_income": total_income, "total_expense": total_expense, "result": result})
