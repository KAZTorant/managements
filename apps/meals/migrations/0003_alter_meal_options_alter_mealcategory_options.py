# Generated by Django 4.2.11 on 2024-05-02 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0002_alter_meal_category_alter_meal_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='meal',
            options={'verbose_name': 'Yemək', 'verbose_name_plural': 'Yeməklər'},
        ),
        migrations.AlterModelOptions(
            name='mealcategory',
            options={'verbose_name': 'Yemək kateqoriyası', 'verbose_name_plural': 'Yemək kateqoriyaları'},
        ),
    ]