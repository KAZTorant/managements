from rangefilter.filters import DateRangeFilter
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from apps.orders.models import Order
from apps.orders.models import OrderItem


# Register the Order model with SimpleHistoryAdmin


@admin.register(Order)
class OrderAdmin(SimpleHistoryAdmin):
    list_display = [
        'table_number',
        'room',
        'waitress',
        'total_price',
        'is_paid',
        'created_at',

    ]
    list_filter = [
        'waitress',
        'table',
        ('created_at', DateRangeFilter),
    ]

    date_hierarchy = 'created_at'

    def table_number(self, order: Order):
        return order.table.number

    def room(self, order: Order):
        return order.table.room

    table_number.short_description = 'Stol'
    room.short_description = 'Zal'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('table', 'waitress')


# Register the OrderItem model


@admin.register(OrderItem)
class OrderItemAdmin(SimpleHistoryAdmin):
    list_display = [
        'order',
        'meal',
        'quantity',
        'price',
        'created_at',
    ]
    list_filter = [
        'meal',
        'order__waitress',
        'order__table',

        ('created_at', DateRangeFilter)
    ]
