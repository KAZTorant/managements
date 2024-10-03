from simple_history.admin import SimpleHistoryAdmin

from django.contrib import admin
from django.db.models import Sum
from django.urls import path
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.utils.dateformat import format
from django.utils.timezone import localtime
from django.utils.html import format_html

from apps.orders.apis.printer import PrinterService
from apps.orders.models import Statistics
from apps.orders.models import Order
from apps.orders.models import OrderItem


class OrderInline(admin.TabularInline):
    # Use the through model for the ManyToMany relationship
    model = Statistics.orders.through
    extra = 0  # No extra empty fields
    can_delete = False  # Prevent deletion of the orders in the inline
    show_change_link = False  # Disable the change link
    fields = [
        'pk',
        'table',
        'total_price',
        'is_paid',
        'created_at',
    ]
    readonly_fields = [
        'pk',
        'table',
        'total_price',
        'is_paid',
        'created_at',
    ]

    def pk(self, obj):
        return obj.id

    def table(self, obj):
        return obj.order.table

    def total_price(self, obj):
        return obj.order.total_price

    def is_paid(self, obj):
        return obj.order.is_paid

    def created_at(self, obj):
        return format(localtime(obj.order.created_at), 'Y-m-d H:i:s')

    pk.short_description = "ID"
    table.short_description = "Stol"
    total_price.short_description = "Məbləğ"
    is_paid.short_description = "Ödənilib"
    is_paid.boolean = True
    created_at.short_description = "Yaradılma Tarixi"


class StatisticsAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'total', 'date', "is_z_checked")
    exclude = ("orders",)
    change_list_template = "admin/statistics_change_list.html"
    list_filter = ("title", "date", "waitress_info")
    readonly_fields = (
        'title', 'date', 'is_z_checked',
        'waitress_info', 'display_order_items')
    inlines = [OrderInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('calculate-till-now/', self.admin_site.admin_view(self.calculate_till_now),
                 name='orders_statistics_calculate_till_now'),
            path('calculate-daily/', self.admin_site.admin_view(self.calculate_daily_stats),
                 name='orders_statistics_calculate_daily'),
            path('calculate-monthly/', self.admin_site.admin_view(self.calculate_monthly_stats),
                 name='orders_statistics_calculate_monthly'),
            path('calculate-yearly/', self.admin_site.admin_view(self.calculate_yearly_stats),
                 name='orders_statistics_calculate_yearly'),
            path('calculate-per-waitress/', self.admin_site.admin_view(
                self.calculate_per_waitress_stats), name='orders_statistics_calculate_per_waitress'),
            path('active-orders/', self.admin_site.admin_view(self.active_orders),
                 name='orders_statistics_active_orders'),  # New URL
        ]
        return custom_urls + urls

    def calculate_per_waitress_stats(self, request):
        Statistics.objects.calculate_per_waitress()
        self.message_user(
            request, "Ofisiant statistikası uğurla əlavə edildi.")
        return HttpResponseRedirect("../")

    def calculate_daily_stats(self, request):
        Statistics.objects.calculate_daily()
        self.message_user(request, "Günlük statistika uğurla əlavə edildi.")
        return HttpResponseRedirect("../")

    def calculate_monthly_stats(self, request):
        Statistics.objects.calculate_monthly()
        self.message_user(request, "Aylıq statistika uğurla əlavə edildi.")
        return HttpResponseRedirect("../")

    def calculate_yearly_stats(self, request):
        Statistics.objects.calculate_yearly()
        self.message_user(request, "İllik statistika uğurla əlavə edildi.")
        return HttpResponseRedirect("../")

    def calculate_till_now(self, request):
        Statistics.objects.calculate_till_now()
        self.message_user(
            request, "Bu günə kimi olan statistika uğurla əlavə edildi.")
        return HttpResponseRedirect("../")

    def z_check(self, obj):
        Statistics.objects.delete_orders_for_statistics_day(obj.date)
        try:
            PrinterService().send_to_printer(text=obj.print_check)
        except Exception as e:
            print("Exception", e)
            return False
        return True

    def z_check_till_now(self, obj):
        obj.delete_orders_till_now()
        try:
            PrinterService().send_to_printer(text=obj.print_check)
        except Exception as e:
            print("Exception", e)
            return False
        return True

    def response_change(self, request, obj):
        if "_z-cek" in request.POST:
            self.z_check(obj=obj)
            self.message_user(request, "Z-Çek hazırlandı %s." % obj.date)
            return HttpResponseRedirect(".")

        if "_z-cek-till-now" in request.POST:
            self.z_check_till_now(obj=obj)
            self.message_user(
                request, "Z-Çek bu günə kimi hazırlandı %s." % obj.date)
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)

    def active_orders(self, request):
        paid_orders_sum = Order.objects.filter(is_paid=True).aggregate(
            total_paid=Sum('total_price'))['total_paid']
        unpaid_orders_sum = Order.objects.filter(is_paid=False).aggregate(
            total_unpaid=Sum('total_price'))['total_unpaid']

        return JsonResponse({
            'total_paid': paid_orders_sum or 0,
            'total_unpaid': unpaid_orders_sum or 0,
        })

    def change_view(self, request, object_id, form_url='', extra_context=None):
        statistic = self.get_object(request, object_id)
        if extra_context is None:
            extra_context = {}
        extra_context['object'] = statistic

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def display_order_items(self, obj):
        # Get all orders related to this statistic
        related_orders = Order.objects.all_orders().filter(statistics=obj)

        # Get all order items related to these orders
        order_items = OrderItem.objects.all_order_items().filter(order__in=related_orders)
        order_items = order_items.values('meal__name').annotate(
            total_quantity=Sum('quantity')
        ).annotate(total_price=Sum('price'))

        if not order_items.exists():
            return "No orders found."
        return self.create_table(order_items)

    def create_table(self, order_items):
        table_html = """
        <hr>
        <table class='table table-striped'>
            <caption style="caption-side: top; text-align: center; font-weight: bold; font-size: 1.2rem; padding-bottom: 8px;">
                Satılmış Məhsullar
            </caption>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Məhsul</th>
                    <th>Miqdar</th>
                    <th>Qiymət</th>
                </tr>
            </thead>
            <tbody>
        """

        total_price, total_quantity = 0, 0
        for index, item in enumerate(order_items, start=1):
            # Summing total price
            total_price += float(item["total_price"])
            total_quantity += int(item["total_quantity"])
            # Adding numbered rows
            table_html += f"""
                <tr>
                    <td>{index}</td>
                    <td>{item["meal__name"]}</td>
                    <td>{item["total_quantity"]}</td>
                    <td>{item["total_price"]}</td>
                </tr>
            """

        # Adding total row at the end
        table_html += f"""
            <tr style="font-weight: bold;">
                <td>Cəmi</td>
                <td></td>
                <td>{total_quantity}</td>
                <td>{total_price}</td>
            </tr>
        """

        table_html += "</tbody></table>"

        return format_html(table_html)

    display_order_items.short_description = ""


admin.site.register(Statistics, StatisticsAdmin)
