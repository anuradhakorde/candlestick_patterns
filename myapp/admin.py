from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser


@admin.register(MyUser)
class MyUserAdmin(UserAdmin):
    """
    Custom admin configuration for MyUser model.
    """
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'phone_number']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'date_of_birth')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'date_of_birth')}),
    )
