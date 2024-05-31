from rangefilter.filters import DateRangeFilter
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from simple_history.utils import get_history_model_for_model
from apps.orders.apis.printer import PrinterService
from apps.orders.models import Order
from apps.orders.models import OrderItem
from apps.orders.models import Statistics
from django.urls import path
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
import datetime

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
class OrderItemAdmin(admin.ModelAdmin):
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

# Register the Statistics model


class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('title', 'total', 'date', "is_z_checked")
    change_list_template = "admin/statistics_change_list.html"
    list_filter = ("title", "date", "waitress_info")

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
            path('todays-orders/', self.admin_site.admin_view(self.todays_orders),
                 name='orders_statistics_todays_orders'),  # New URL
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

    def todays_orders(self, request):
        today = timezone.now().date()
        start_of_day = timezone.make_aware(
            datetime.datetime.combine(today, datetime.time.min))
        end_of_day = timezone.make_aware(
            datetime.datetime.combine(today, datetime.time.max))

        paid_orders_sum = Order.objects.filter(created_at__range=(
            start_of_day, end_of_day), is_paid=True).aggregate(total_paid=Sum('total_price'))['total_paid'] or 0
        unpaid_orders_sum = Order.objects.filter(created_at__range=(
            start_of_day, end_of_day), is_paid=False).aggregate(total_unpaid=Sum('total_price'))['total_unpaid'] or 0

        return JsonResponse({
            'total_paid': paid_orders_sum,
            'total_unpaid': unpaid_orders_sum,
        })

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        if extra_context is None:
            extra_context = {}
        extra_context['object'] = obj
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


admin.site.register(Statistics, StatisticsAdmin)

# Dynamically get the historical models
HistoricalOrder = get_history_model_for_model(Order)
HistoricalOrderItem = get_history_model_for_model(OrderItem)

HistoricalOrder._meta.verbose_name = 'Sifariş tarixçəsi'
HistoricalOrder._meta.verbose_name_plural = 'Sifarişlər tarixçəsi'


HistoricalOrderItem._meta.verbose_name = 'Sifariş məhsulu tarixçəsi'
HistoricalOrderItem._meta.verbose_name_plural = 'Sifariş məhsulları tarixçəsi'

# Register the historical models in the admin


@admin.register(HistoricalOrder)
class HistoricalOrderAdmin(admin.ModelAdmin):
    list_display = [
        'table',
        'is_paid',
        'waitress',
        'total_price',
        'history_type',
        'created_at',
    ]
    list_filter = [
        'waitress',
        'table',
        ('created_at', DateRangeFilter)
    ]


@admin.register(HistoricalOrderItem)
class HistoricalOrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order',
        'meal',
        'quantity',
        'price',
        'history_type',
        'created_at',
    ]
    list_filter = [
        'meal',
        'order__waitress',
        'order__table',
        ('created_at', DateRangeFilter)
    ]

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            queryset = response.context_data['cl'].queryset
            aggregated_data = queryset.aggregate(
                total_quantity=Sum('quantity'),
                total_price=Sum('price')
            )
            extra_context = extra_context or {}
            extra_context['total_quantity'] = aggregated_data['total_quantity']
            extra_context['total_price'] = aggregated_data['total_price']
            response.context_data.update(extra_context)
        except (AttributeError, KeyError):
            pass
        return response
