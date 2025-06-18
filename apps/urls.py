from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, EntryLogViewSet, ExitLogViewSet

router = DefaultRouter()
router.register('vehicles', VehicleViewSet)
router.register('entries', EntryLogViewSet)
router.register('exits', ExitLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
