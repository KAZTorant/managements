from django.contrib import admin
from django.db.models import Subquery
from django.db.models import OuterRef
from django.db.models import Sum

from rangefilter.filters import DateRangeFilter
from simple_history.utils import get_history_model_for_model

from apps.orders.models import Order
from apps.orders.models import OrderItem

# Dynamically get the historical models
HistoricalOrder = get_history_model_for_model(Order)
HistoricalOrderItem = get_history_model_for_model(OrderItem)

HistoricalOrder._meta.verbose_name = 'Arxiv (Sifariş)'
HistoricalOrder._meta.verbose_name_plural = 'Arxiv (Sifarişlər) 🎞️'


HistoricalOrderItem._meta.verbose_name = 'Arxiv (Sifariş məhsulu)'
HistoricalOrderItem._meta.verbose_name_plural = 'Arxiv (Sifariş məhsulu) 🎞️'

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
        'id',
        'order',
        'meal',
        'quantity',
        'price',
        'is_deleted_by_adminstrator',
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

            # Create a subquery to get the latest history_date for each id
            subquery = queryset.exclude(is_deleted_by_adminstrator=True).filter(id=OuterRef('id')).order_by(
                '-history_date').values('history_date')[:1]

            # Filter the queryset to include only the latest records
            latest_records = queryset.filter(history_date=Subquery(subquery))

            # Perform the aggregation on the filtered queryset
            aggregated_data = latest_records.aggregate(
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
