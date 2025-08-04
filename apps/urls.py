from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from .views import (
    VehicleViewSet,
    ExitLogViewSet,
    ExceptionalTransportsViewSet,
    index_view,
    vehicle_list_view,
    CustomTokenObtainPairView,
    ManualEntryView,
    vehicle_detail_view,
    FineStatusViewSet,
    VehicleOutANPRView,
    VehicleINANPRView,
    FullEntryExitStatisticsAPIView,
    EntryViewSet, EntryByPlateAPIView, DRBReadAPIView,
)

router = DefaultRouter()
router.register("vehicles", VehicleViewSet)
router.register(r'exceptional-transports', ExceptionalTransportsViewSet, basename='exceptional-transport')
router.register("entries", EntryViewSet)
# router.register('entries-vehicle', EntryViewSet)
router.register("exits", ExitLogViewSet, basename='exit')
router.register("fine-status", FineStatusViewSet)

urlpatterns = [
    path("", index_view, name="index"),
    path("kiritish/", views.manual_entry_view, name="entry_form"),

    path("vehicles/", vehicle_list_view, name="vehicles"),
    path(
        "kiritish/",
        TemplateView.as_view(template_name="entry_form.html"),
        name="entry_form",
    ),
    path(
        "chiqarish/",
        TemplateView.as_view(template_name="exit_form.html"),
        name="exit-form",
    ),
    path("login/", TemplateView.as_view(template_name="login.html"), name="login"),
    # path('logout/', logout_view, name='logout'),
    path(
        "kirgan-mashinalar/",
        TemplateView.as_view(template_name="entry_logs.html"),
        name="entry-logs",
    ),
    path(
        "chiqqan-mashinalar/",
        TemplateView.as_view(template_name="exit_logs.html"),
        name="exit-logs",
    ),
    path(
        "maxsus-mashinalar/",
        TemplateView.as_view(template_name="exceptional_transports.html"),
        name="exceptional-transports",
    ),
    path('api/camera/in/', VehicleINANPRView.as_view(), name="camera_in"),
    path('api/camera/out/', VehicleOutANPRView.as_view(), name="camera_out"),
    path("api/statistics/full/", FullEntryExitStatisticsAPIView.as_view(), name="full-statistics"),
    path('api/drb-read/', DRBReadAPIView.as_view(), name='drb-read'),
    path("users/", TemplateView.as_view(template_name="users.html"), name="users"),
    path("report/", TemplateView.as_view(template_name="report.html"), name="report"),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/entries/<str:plate>/", EntryByPlateAPIView.as_view(), name="entry-by-plate"),
    path("api/manual-entry/", ManualEntryView.as_view(), name="manual_entry"),
    path("vehicle-detail/", vehicle_detail_view, name="vehicle_detail"),
    path("api/", include(router.urls)),
]
