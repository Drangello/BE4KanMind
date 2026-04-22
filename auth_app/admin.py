from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'fullname', 'is_staff', 'is_active']
    search_fields = ['email', 'username', 'fullname']
    
    # Optional fieldsets to show fullname if we use standard UserAdmin forms
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Profil-Daten', {'fields': ('fullname',)}),
    )

admin.site.register(User, CustomUserAdmin)
