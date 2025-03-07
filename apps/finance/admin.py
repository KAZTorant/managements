from django.contrib import admin

from apps.finance.models import Expense
from apps.finance.models import Income

admin.site.register(Expense)
admin.site.register(Income)
