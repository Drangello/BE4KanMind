from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'fullname', 'is_staff', 'is_active']
    search_fields = ['email', 'username', 'fullname']

    fieldsets = UserAdmin.fieldsets + (
        ('Extra Profil-Daten', {'fields': ('fullname',)}),
    )

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        return request.user.is_staff


admin.site.register(User, CustomUserAdmin)