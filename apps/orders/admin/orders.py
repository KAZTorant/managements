from rangefilter.filters import DateRangeFilter
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from apps.orders.models import Order
from apps.orders.models import OrderItem


# Register the Order model with SimpleHistoryAdmin


@admin.register(Order)
class OrderAdmin(SimpleHistoryAdmin):
    list_display = [
        'table',

        'waitress',
        'total_price',
        'created_at',
        'is_paid',
        'is_active_order',
    ]
    list_filter = [
        'waitress',
        'table',
        ('created_at', DateRangeFilter)
    ]

    date_hierarchy = 'created_at'

    def is_active_order(self, obj):
        # Considering an order as active if it has not been paid yet
        return not obj.is_paid

    is_active_order.short_description = 'Aktiv'
    # This will display a nice icon instead of True/False
    is_active_order.boolean = True

    def get_queryset(self, request):
        # Optimizing queryset to include related data to reduce database hits
        queryset = super().get_queryset(request).select_related('table', 'waitress')
        return queryset

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
