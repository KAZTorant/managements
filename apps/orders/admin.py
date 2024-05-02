from apps.orders.models import Order
from apps.orders.models import OrderItem

from django.contrib import admin


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'is_active_order',
                    'waitress', 'total_price', 'created_at')
    list_filter = ('is_paid', 'waitress', 'created_at')
    search_fields = ('table__number', 'waitress__username')
    date_hierarchy = 'created_at'

    def is_active_order(self, obj):
        # Considering an order as active if it has not been paid yet
        return not obj.is_paid
    is_active_order.short_description = 'Is Active'
    # This will display a nice icon instead of True/False
    is_active_order.boolean = True

    def get_queryset(self, request):
        # Optimizing queryset to include related data to reduce database hits
        queryset = super().get_queryset(request).select_related('table', 'waitress')
        return queryset


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
