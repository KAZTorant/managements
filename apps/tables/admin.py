from django.contrib import admin
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404, render
from django.urls import path
from apps.orders.models import Order

from apps.tables.models import Table
from apps.tables.models import Room

admin.site.register(Room)


# @admin.register(Table)
# class TableAdmin(admin.ModelAdmin):
#     list_display = ('number', 'room', 'current_waitress', 'current_order_status',
#                     'total_order_price',  'display_total_price')
#     search_fields = ('number', 'room__name')
#     ordering = ('number', 'room__name')
#     list_filter = ('room', 'orders__is_paid', 'orders__is_check_printed')

#     def current_waitress(self, obj):
#         # Fetches the waitress from the current active order if available
#         order = obj.current_order
#         return order.waitress if order else None
#     current_waitress.short_description = 'Ofisiant'

#     def current_order_status(self, obj):
#         # Checks if there is an active (unpaid) order
#         order = obj.current_order
#         return True if order and not order.is_paid else False
#     current_order_status.short_description = 'Aktiv Sifariş'
#     current_order_status.boolean = True

#     def total_order_price(self, obj):
#         # Displays the total price of the current order
#         order = obj.current_order
#         return order.total_price if order else '0.00'
#     total_order_price.short_description = 'Cari Sifarişin Qiyməti'

#     def display_total_price(self, obj):
#         # Aggregate total price from all orders associated with the table
#         total = Order.objects.filter(table=obj).aggregate(
#             models.Sum('total_price'))['total_price__sum']
#         return total or '0.00'
#     display_total_price.short_description = 'Bütün Sifarişlərin Qiyməti'

#     def get_queryset(self, request):
#         # Optimizing queryset to prefetch related orders and reduce database hits
#         queryset = super().get_queryset(request).prefetch_related(
#             'orders').select_related('room')
#         return queryset


class CustomTableAdmin(admin.ModelAdmin):
    change_list_template = "admin/tables_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('table/<int:table_id>/orders/',
                 self.admin_site.admin_view(self.orders_view), name='table_active_order'),
        ]
        return custom_urls + urls

    def orders_view(self, request, table_id):
        table = get_object_or_404(Table, pk=table_id)
        orders = Order.objects.filter(table=table, is_paid=False)
        total_quantity = orders.aggregate(total_quantity=Sum(
            'order_items__quantity'))['total_quantity'] or 0
        total_price = orders.aggregate(total_price=Sum(
            F('order_items__quantity') * F('order_items__price')))['total_price'] or 0

        return render(
            request,
            'admin/orders_modal.html',
            {
                'table': table,
                'orders': orders,
                'total_quantity': total_quantity,
                'total_price': total_price,
            }
        )

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            cl = response.context_data['cl']
            cl.result_list = cl.result_list.order_by('room').order_by('number')
            cl.rooms = Room.objects.all()
            for table in cl.result_list:
                table.has_unpaid_orders = Order.objects.exclude(
                    is_deleted=True).filter(table=table, is_paid=False).exists()
        except (AttributeError, KeyError):
            pass
        return response


admin.site.register(Table, CustomTableAdmin)
