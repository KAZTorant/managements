# Generated by Django 4.2.11 on 2024-05-13 20:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0015_alter_order_created_at_alter_orderitem_created_at_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statistics',
            options={'verbose_name': 'Statistika', 'verbose_name_plural': 'Statistikalar'},
        ),
    ]
