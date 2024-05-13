from django.db import models

from apps.commons.models import DateTimeModel
from django.utils import timezone
from django.db.models import Sum

from apps.orders.models import Order

import datetime, calendar
from datetime import timedelta


class StatisticsManager(models.Manager):

    def calculate_per_waitress(self, date=None):
        if not date:
            date = timezone.localdate() - timedelta(days=1)  # Default to today if no date is provided
        
        waitresses_orders = Order.objects.filter(
            created_at__date=date,
            is_paid=True,  # Considering only paid orders
            waitress__isnull=False  # Ensuring orders have an assigned waitress
        ).values('waitress', 'waitress__username', 'waitress__first_name', 'waitress__last_name').annotate(total_price=Sum('total_price'))

        for order in waitresses_orders:
            waitress_info = f"{order['waitress__username']} - {order['waitress__first_name']} {order['waitress__last_name']}"

            obj, created = self.update_or_create(
                title='per_waitress',
                date=date,
                waitress_info=waitress_info,
                defaults={
                    'total': order['total_price'],
                }
            )

    def calculate_daily(self, date=None):
        if not date:
            date = timezone.localdate() - timedelta(days=1) # Default to today if no date is provided

        self.calculate_per_waitress(date=date)

        existing_stat = self.filter(title='daily', date=date).first()
        if not existing_stat:
            start_of_day = timezone.make_aware(datetime.datetime.combine(date, datetime.time.min))
            end_of_day = timezone.make_aware(datetime.datetime.combine(date, datetime.time.max))

            daily_total = Order.objects.filter(created_at__range=(start_of_day, end_of_day), is_paid=True).aggregate(Sum('total_price'))['total_price__sum'] or 0

            if not daily_total:
                return

            obj, created = self.update_or_create(
                title='daily',
                date=date,
                defaults={'total': daily_total}
            )

        return existing_stat or obj

    def calculate_monthly(self, date=None):
        if not date:
            date = timezone.localdate() - timedelta(days=1) # Default to this month if no date is provided
        first_of_month = date.replace(day=1)
        last_day = date.replace(day=calendar.monthrange(date.year, date.month)[1])

        for single_date in (first_of_month + datetime.timedelta(days=n) for n in range((last_day - first_of_month).days + 1)):
            self.calculate_daily(single_date)

        monthly_total = self.filter(title='daily', date__range=[first_of_month, last_day]).aggregate(Sum('total'))['total__sum'] or 0
        
        if not monthly_total:
            return
        
        monthly_stat, created = self.update_or_create(
            title='monthly',
            date=first_of_month,
            defaults={'total': monthly_total}
        )
        return monthly_stat

    def calculate_yearly(self, date=None):
        if not date:
            date = timezone.localdate() - timedelta(days=1) # Default to this year if no date is provided
        first_of_year = date.replace(month=1, day=1)
        last_month = date.month

        for month in range(1, last_month + 1):
            month_date = first_of_year.replace(month=month)
            self.calculate_monthly(month_date)

        yearly_total = self.filter(title='monthly', date__year=date.year).aggregate(Sum('total'))['total__sum'] or 0

        if not yearly_total:
            return
        
        yearly_stat, created = self.update_or_create(
            title='yearly',
            date=first_of_year,
            defaults={'total': yearly_total}
        )
        return yearly_stat

    def delete_orders_for_statistics_day(self, date):
        # First check if statistics exist for the day, if not calculate them
        self.calculate_daily(date)

        start_of_day = timezone.make_aware(datetime.datetime.combine(date, datetime.time.min))
        end_of_day = timezone.make_aware(datetime.datetime.combine(date, datetime.time.max))

        # Filter and delete orders within the specified range that are paid
        orders = Order.objects.filter(created_at__range=(start_of_day, end_of_day), is_paid=True)
        count = orders.count()  # Count orders before deletion for reporting
        orders.delete()
        return count  # Return the number of deleted orders for confirmation/logging


class Statistics(DateTimeModel, models.Model):
    TITLE_CHOICES = (
        ("daily", "Günlük"),
        ("monthly", "Aylıq"),
        ("yearly", "İllik"),
        ("per_waitress", "Ofisianta görə")
    )

    title = models.CharField(
        max_length=32,
        choices=TITLE_CHOICES,
        default=TITLE_CHOICES[0][0],
        verbose_name="Başlıq"
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ümumi")
    date = models.DateField(default=timezone.now, verbose_name="Tarix")

    waitress_info = models.CharField(
        max_length=90, blank=True, null=True, 
        help_text="Ofisiant kodu və adı.",
        verbose_name="Ofisiant"
    )

    objects = StatisticsManager()

    class Meta:
        verbose_name = "Statistika"
        verbose_name_plural = "Statistikalar"

    def __str__(self) -> str:
        if self.title == "per_waitress":
            return f"{self.waitress_info} Statistics for {self.date}"
        return f"{self.title} Statistics for {self.date}"

    @property
    def print_check(self):
        return f"""
            Tarix:{self.date.strftime('%d.%m.%Y %H:%M:%S')}
            Məbləğ: {self.total}
            Başlıq: {self.get_title_display()}
        """

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
