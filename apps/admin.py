from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    CustomUser,
    Vehicle,
    ExitLog,
    FineStatus,
    Area,
    ExceptionalTransports,
    Entry,
)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Shaxsiy ma'lumotlar"), {"fields": ("full_name",)}),
        (
            _("Ruxsatlar"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Muhim sanalar"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
    readonly_fields = (
        "date_joined",
        "last_login",
    )  # 🔹 Faqat ko‘rsatilsin, lekin tahrir qilib bo‘lmasin

    list_display = ("id", "phone", "full_name", "is_superuser", "is_staff", "is_active")
    search_fields = ("phone", "username")
    ordering = ("username",)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("id", "plate_number")
    search_fields = (["plate_number"])


@admin.register(ExceptionalTransports)
class ExceptionalTransportsAdmin(admin.ModelAdmin):
    list_display = ("id", "plate_number", "owner_name", "phone_number")
    search_fields = ("plate_number", "owner_name", "phone_numbero")


@admin.register(ExitLog)
class ExitLogAdmin(admin.ModelAdmin):
    list_display = ("id", "entry", "vehicle", "timestamp", "yard_fee_paid", "calculated_fee")
    list_filter = ("timestamp", "yard_fee_paid")
    search_fields = ("vehicle__plate_number",)

    def calculated_fee(self, obj):
        return obj.calculate_yard_fee()

    calculated_fee.short_description = "Hisoblangan to‘lov"


@admin.register(FineStatus)
class FineStatusAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "has_fine", "is_paid")
    list_filter = ("has_fine", "is_paid")
    search_fields = ("vehicle__plate_number",)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['area_id', 'daily_fee', 'created_at']
    search_fields = ['area_id']

    def has_add_permission(self, request):
        return not Area.objects.exists()


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ["plate_number", "timestamp", "is_manual"]
    readonly_fields = [
        "photo_front",
        "photo_rear",
        "photo_left",
        "photo_right",
        "no_plate_number",
    ]

    def image_preview(self, obj):
        if obj.photo_front:
            return format_html('<img src="{}" width="100" />', obj.photo_front.url)
        return "-"

    image_preview.short_description = "Oldi rasm"
