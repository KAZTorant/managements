from apps.orders.models import Order
from apps.orders.models import OrderItem

from django.contrib import admin

admin.site.register(Order)
admin.site.register(OrderItem)
