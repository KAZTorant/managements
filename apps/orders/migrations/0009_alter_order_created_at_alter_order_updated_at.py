# Generated by Django 4.2.11 on 2024-05-13 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_orderitem_created_at_orderitem_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
