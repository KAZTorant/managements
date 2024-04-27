from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.tables.models import Table


@receiver(pre_save, sender=Table)
def set_table_number(sender, instance: Table, *args, **kwargs):
    if not instance.number and instance.room:
        instance.number = f"Masa {instance.room.tables.count() + 1}"
