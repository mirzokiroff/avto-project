from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    CustomUser, Vehicle, EntryLog, ExitLog,
    FineStatus, Camera, Area, ExceptionalTransports
)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        (_("Shaxsiy ma'lumotlar"), {"fields": ("full_name",)}),
        (_("Ruxsatlar"), {"fields": ("is_active", "is_staff", "is_superuser", "is_admin", "is_guard")}),
        (_("Muhim sanalar"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone", "full_name", "password1", "password2"),
        }),
    )
    list_display = ("id", "phone", "full_name", "is_admin", "is_guard", "is_superuser")
    search_fields = ("phone", "full_name")
    ordering = ("-id",)
    exclude = ("username", "email", "first_name", "last_name", "groups", "user_permissions", "date_joined")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("id", "plate_number", "owner_name", "is_evacuator", "is_whitelisted")
    search_fields = ("plate_number", "owner_name")


@admin.register(ExceptionalTransports)
class ExceptionalTransportsAdmin(admin.ModelAdmin):
    list_display = ("id", "plate_number", "owner_name")
    search_fields = ("plate_number", "owner_name")



@admin.register(EntryLog)
class EntryLogAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "entry_time", "is_manual", "entry_by")
    list_filter = ("is_manual", "entry_time")
    search_fields = ("vehicle__plate_number",)


@admin.register(ExitLog)
class ExitLogAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "exit_time", "paid_amount", "approved_by")
    list_filter = ("exit_time",)
    search_fields = ("vehicle__plate_number",)


@admin.register(FineStatus)
class FineStatusAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "has_fine", "is_paid")
    list_filter = ("has_fine", "is_paid")
    search_fields = ("vehicle__plate_number",)


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ("name", "ip_address", "port", "type", "is_active")
    list_filter = ("type", "is_active")
    search_fields = ("name", "ip_address")

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("area_id", "created_at")

    def has_add_permission(self, request):
        return not Area.objects.exists()
