from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import VehicleViewSet, EntryLogViewSet, ExitLogViewSet, ExceptionalTransportsViewSet, index_view, \
    vehicle_list_view, MyTokenObtainPairView, CustomTokenObtainPairView, ManualEntryView, vehicle_detail_view, \
    FineStatusViewSet

router = DefaultRouter()
router.register('vehicles', VehicleViewSet)
router.register('exceptional-transports', ExceptionalTransportsViewSet)
router.register('entries', EntryLogViewSet)
router.register('exits', ExitLogViewSet)
router.register('fine-status', FineStatusViewSet)

urlpatterns = [
    path('', index_view, name='index'),
    path('vehicles/', vehicle_list_view, name='vehicles'),
    path('entry/', TemplateView.as_view(template_name="entry_form.html"), name="entry_form"),
    path('login/', TemplateView.as_view(template_name="login.html"), name="login"),
    path('kirgan-mashinalar/', TemplateView.as_view(template_name='entry_logs.html'), name='entry-logs'),
    path('chiqqan-mashinalar/', TemplateView.as_view(template_name='exit_logs.html'), name='exit-logs'),
    path('maxsus-mashinalar/', TemplateView.as_view(template_name='exceptional_transports.html'),
         name='exceptional-transports'),
    path('users/', TemplateView.as_view(template_name='users.html'), name='users'),
    path('report/', TemplateView.as_view(template_name='report.html'), name='report'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/entries/', ManualEntryView.as_view(), name='manual_entry'),
    path('vehicle-detail/', vehicle_detail_view, name='vehicle_detail'),

    path('api/', include(router.urls)),
]
