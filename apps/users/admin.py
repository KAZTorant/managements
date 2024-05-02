from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'type', 'first_name',
                    'last_name', 'is_staff', 'is_active')
    list_filter = ('type', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', "first_name", "last_name",)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups',)}),
        ('User Type', {'fields': ('type',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'type', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('username',)
    ordering = ('username',)


# Register the custom admin class
admin.site.register(User, CustomUserAdmin)
