from rest_framework import generics
from django.db.models import Sum
from rest_framework.response import Response
from datetime import date, timedelta

from apps.finance.models import Income, Expense
from apps.finance.serializers import IncomeSerializer, ExpenseSerializer


class IncomeCreateView(generics.CreateAPIView):
    start_date = date.today() - timedelta(days=30)
    queryset = Income.objects.filter(date__gte=start_date)
    serializer_class = IncomeSerializer


class ExpenseCreateView(generics.CreateAPIView):
    start_date = date.today() - timedelta(days=30)
    queryset = Expense.objects.filter(date__gte=start_date)
    serializer_class = ExpenseSerializer


class IncomeListView(generics.ListAPIView):
    start_date = date.today() - timedelta(days=30)
    queryset = Income.objects.filter(date__gte=start_date)
    serializer_class = IncomeSerializer


class ExpenseListView(generics.ListAPIView):
    start_date = date.today() - timedelta(days=30)
    queryset = Expense.objects.filter(date__gte=start_date)
    serializer_class = ExpenseSerializer


class DailyResultView(generics.GenericAPIView):
    def get(self, request):
        today = date.today()
        total_income = Income.objects.filter(date=today).aggregate(Sum('amount'))[
            'amount__sum'] or 0
        total_expense = Expense.objects.filter(date=today).aggregate(Sum('amount'))[
            'amount__sum'] or 0
        result = total_income - total_expense
        return Response({"date": today, "total_income": total_income, "total_expense": total_expense, "result": result})


class AllResultsView(generics.GenericAPIView):
    def get(self, request):
        results = []
        start_date = date.today() - timedelta(days=30)
        unique_dates = Income.objects.filter(
            date__gte=start_date).values_list('date', flat=True).distinct()
        for day in unique_dates:
            total_income = Income.objects.filter(date=day).aggregate(Sum('amount'))[
                'amount__sum'] or 0
            total_expense = Expense.objects.filter(date=day).aggregate(Sum('amount'))[
                'amount__sum'] or 0
            result = total_income - total_expense
            results.append({"date": day, "total_income": total_income,
                           "total_expense": total_expense, "result": result})
        return Response(results)
