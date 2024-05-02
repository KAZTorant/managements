from django.contrib import admin
from django.db import models
from apps.orders.models import Order

from apps.tables.models import Table
from apps.tables.models import Room

admin.site.register(Room)


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'room', 'current_waitress', 'current_order_status',
                    'total_order_price',  'display_total_price')
    search_fields = ('number', 'room__name')
    ordering = ('number', 'room__name')
    list_filter = ('room', 'orders__is_paid', 'orders__is_check_printed')

    def current_waitress(self, obj):
        # Fetches the waitress from the current active order if available
        order = obj.current_order
        return order.waitress if order else None
    current_waitress.short_description = 'Ofisiant'

    def current_order_status(self, obj):
        # Checks if there is an active (unpaid) order
        order = obj.current_order
        return True if order and not order.is_paid else False
    current_order_status.short_description = 'Aktiv Sifariş'
    current_order_status.boolean = True

    def total_order_price(self, obj):
        # Displays the total price of the current order
        order = obj.current_order
        return order.total_price if order else '0.00'
    total_order_price.short_description = 'Cari Sifarişin Qiyməti'

    def display_total_price(self, obj):
        # Aggregate total price from all orders associated with the table
        total = Order.objects.filter(table=obj).aggregate(
            models.Sum('total_price'))['total_price__sum']
        return total or '0.00'
    display_total_price.short_description = 'Bütün Sifarişlərin Qiyməti'

    def get_queryset(self, request):
        # Optimizing queryset to prefetch related orders and reduce database hits
        queryset = super().get_queryset(request).prefetch_related(
            'orders').select_related('room')
        return queryset
