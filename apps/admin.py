from django.contrib import admin
from .models import CustomUser, Camera, Avto, Area


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    exclude = ("groups", "email", "last_login", "date_joined")

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False
    
    def has_change_permission(self, request, obj = None):
        if request.user.is_superuser:
            return True
        return False

    def has_delete_permission(self, request, obj = None):
        if request.user.is_superuser:
            return True
        return False


@admin.register(Area)
class ProductAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if Area.objects.exists():
            return False
        return True


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False
    
    def has_change_permission(self, request, obj = None):
        if request.user.is_superuser:
            return True
        return False

    def has_delete_permission(self, request, obj = None):
        if request.user.is_superuser:
            return True
        return False


@admin.register(Avto)
class AvtoAdmin(admin.ModelAdmin):
    pass
