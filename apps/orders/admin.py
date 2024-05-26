from apps.orders.apis.printer import PrinterService
from apps.orders.models import Order
from apps.orders.models import OrderItem
from apps.orders.models import Statistics

from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum

import datetime


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'is_active_order',
                    'waitress', 'total_price', 'created_at')
    list_filter = ('is_paid', 'waitress', 'created_at')
    search_fields = ('table__number', 'waitress__username')
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


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)


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
            request, "Bu günə kimi olan statistika uğurla əlavə edildi."
        )
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
            # Optionally redirect or perform additional actions
            return HttpResponseRedirect(".")

        if "_z-cek-till-now" in request.POST:
            self.z_check_till_now(obj=obj)
            self.message_user(
                request, "Z-Çek bu günə kimi hazırlandı %s." % obj.date)
            # Optionally redirect or perform additional actions
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
