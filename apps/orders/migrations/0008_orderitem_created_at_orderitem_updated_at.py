# Generated by Django 4.2.11 on 2024-05-10 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_orderitem_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
