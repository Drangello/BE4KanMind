from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'fullname', 'is_staff', 'is_active']
    search_fields = ['email', 'username', 'fullname']
    list_filter = ['is_staff', 'is_active']

    fieldsets = UserAdmin.fieldsets + (
        ('Extra Profil-Daten', {'fields': ('fullname',)}),
    )

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj == request.user:
            return False
        return request.user.is_staff or request.user.is_superuser


admin.site.register(User, CustomUserAdmin)