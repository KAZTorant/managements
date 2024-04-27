from django.contrib import admin

from apps.tables.models import Table
from apps.tables.models import Room

admin.site.register(Room)
admin.site.register(Table)
