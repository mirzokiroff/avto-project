from django.contrib import admin
from .models import Area


@admin.register(Area)
class ProductAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if Area.objects.exists():
            return False
        return True
