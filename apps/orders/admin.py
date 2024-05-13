from apps.orders.models import Order
from apps.orders.models import OrderItem
from apps.orders.models import Statistics

from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect


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
    list_display = ('title', 'total', 'date', "waitress_info")
    change_list_template = "admin/statistics_change_list.html"
    list_filter = ("title", "date", "waitress_info")
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('calculate-daily/', self.admin_site.admin_view(self.calculate_daily_stats), name='orders_statistics_calculate_daily'),
            path('calculate-monthly/', self.admin_site.admin_view(self.calculate_monthly_stats), name='orders_statistics_calculate_monthly'),
            path('calculate-yearly/', self.admin_site.admin_view(self.calculate_yearly_stats), name='orders_statistics_calculate_yearly'),
            path('calculate-per-waitress/', self.admin_site.admin_view(self.calculate_per_waitress_stats), name='orders_statistics_calculate_per_waitress'),
        ]
        return custom_urls + urls

    def calculate_per_waitress_stats(self, request):
        Statistics.objects.calculate_per_waitress()
        self.message_user(request, "Ofisiant statistikası uğurla əlavə edildi.")
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


admin.site.register(Statistics, StatisticsAdmin)
