from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.timezone import now
from rest_framework.settings import api_settings

from .filters import ExitLogFilter
from .models import Vehicle, EntryLog, ExitLog, FineStatus
from .serializers import *
from .services.gai_api import check_with_gai
from .services.payment import calculate_fee
from .services.barrier import open_barrier
from .services.pdf_generator import generate_receipt_pdf
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_csv import renderers as csv_renderers


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


class EntryLogViewSet(viewsets.ModelViewSet):
    queryset = EntryLog.objects.all()
    serializer_class = EntryLogSerializer

    def create(self, request, *args, **kwargs):
        plate_number = request.data.get('plate_number')
        is_manual = request.data.get('is_manual', False)
        photo = request.data.get('photo')

        vehicle, _ = Vehicle.objects.get_or_create(plate_number=plate_number)
        entry = EntryLog.objects.create(
            vehicle=vehicle,
            photo=photo,
            is_manual=is_manual,
            entry_by=request.user
        )

        if not vehicle.is_whitelisted:
            fined, paid = check_with_gai(plate_number)
            FineStatus.objects.update_or_create(
                vehicle=vehicle,
                defaults={'has_fine': fined, 'is_paid': paid}
            )

        return Response(EntryLogSerializer(entry).data)


class ExitLogViewSet(viewsets.ModelViewSet):
    queryset = ExitLog.objects.all()
    serializer_class = ExitLogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExitLogFilter
    renderer_classes = [csv_renderers.CSVRenderer] + api_settings.DEFAULT_RENDERER_CLASSES

    @action(detail=False, methods=['post'])
    def process_exit(self, request):
        plate_number = request.data.get('plate_number')
        photo = request.data.get('photo')
        barrier_device_id = request.data.get('barrier_id')

        if not plate_number:
            return Response({"error": "plate_number is required"}, status=400)

        try:
            vehicle = Vehicle.objects.get(plate_number=plate_number)
        except Vehicle.DoesNotExist:
            return Response({"error": "Vehicle not found"}, status=404)

        try:
            entry = EntryLog.objects.filter(vehicle=vehicle).latest('entry_time')
        except EntryLog.DoesNotExist:
            return Response({"error": "No entry log found for this vehicle"}, status=404)

        exit_time = now()
        amount = calculate_fee(entry.entry_time, exit_time)

        if not vehicle.is_whitelisted:
            fine_status = FineStatus.objects.filter(vehicle=vehicle).first()
            if fine_status and not fine_status.is_paid:
                return Response({"error": "Fine not paid"}, status=403)

        log = ExitLog.objects.create(
            vehicle=vehicle,
            photo=photo,
            exit_time=exit_time,
            paid_amount=amount,
            approved_by=request.user
        )

        try:
            receipt_path = generate_receipt_pdf(vehicle, entry.entry_time, exit_time, amount)
            log.receipt = receipt_path
            log.save()
        except Exception as e:
            return Response({"error": f"PDF generation failed: {str(e)}"}, status=500)

        success = open_barrier(barrier_device_id)
        if not success:
            return Response({"error": "Failed to open barrier"}, status=500)

        return Response(ExitLogSerializer(log).data)
