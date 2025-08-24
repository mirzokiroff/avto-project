from django.conf import settings
import xml.etree.ElementTree as ET
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdminOrReadOnly
from .serializers import *
from .utils.yhxbb_api import YHXBB


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["plate_number"]

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        area = Area.objects.first().area_id
        serializer.save(area=area)


class ExceptionalTransportsViewSet(viewsets.ModelViewSet):
    queryset = ExceptionalTransports.objects.all()
    serializer_class = ExceptionalTransportsSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["plate_number"]


class ExitLogViewSet(viewsets.ModelViewSet):
    queryset = ExitLog.objects.all().order_by("-timestamp")
    serializer_class = ExitLogSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(approved_by=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        entry_id = self.request.query_params.get("entry")
        if entry_id:
            queryset = queryset.filter(entry_id=entry_id)
        return queryset

    def create(self, request, *args, **kwargs):
        entry_id = request.data.get("entry")
        # vehicle_id = request.data.get("vehicle")

        try:
            entry = Entry.objects.get(id=entry_id)
            vehicle = entry.vehicle
        except Entry.DoesNotExist:
            return Response(
                {"detail": "Entry topilmadi."}, status=status.HTTP_404_NOT_FOUND
            )
        except Vehicle.DoesNotExist:
            return Response(
                {"detail": "Vehicle topilmadi."}, status=status.HTTP_404_NOT_FOUND
            )

        now = timezone.now()
        duration = now - entry.timestamp
        total_minutes = int(duration.total_seconds() // 60)

        # Fayllar
        photo_front = request.FILES.get("exit_photo_front")
        photo_rear = request.FILES.get("exit_photo_rear")
        photo_left = request.FILES.get("exit_photo_left")
        photo_right = request.FILES.get("exit_photo_right")

        # ✅ To‘lov boolean ga aylantirildi
        yard_fee_paid = request.data.get("yard_fee_paid", "false").lower() == "true"

        # ✅ is_manual_entry ni entry modelidan olish
        is_manual_entry = entry.is_manual

        exit_log = ExitLog.objects.create(
            vehicle=vehicle,
            entry=entry,
            photo_front_exit=photo_front,
            photo_rear_exit=photo_rear,
            photo_left_exit=photo_left,
            photo_right_exit=photo_right,
            total_minutes=total_minutes,
            yard_fee_paid=yard_fee_paid,
            area=vehicle.area,
            is_manual_entry=is_manual_entry,
            is_manual_exit=True
        )

        serializer = self.get_serializer(exit_log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["role"] = "admin" if self.user.is_superuser else "user"
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ManualEntryView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = EntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FineStatusViewSet(viewsets.ModelViewSet):
    queryset = FineStatus.objects.all()
    serializer_class = FineStatusSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["vehicle"]


def index_view(request):
    query = request.GET.get("search")
    vehicles = []

    if query:
        sanitized_query = ''.join(filter(str.isalnum, query.upper()))
        vehicles = Vehicle.objects.filter(plate_number__icontains=sanitized_query)

    return render(request, 'index.html', {
        "vehicles": vehicles,
    })


def vehicle_list_view(request):
    vehicles = Vehicle.objects.all()
    return render(request, "vehicles.html", {"vehicles": vehicles})


def vehicle_detail_view(request):
    return render(request, "vehicle_detail.html")


@login_required
def manual_entry_view(request):
    position_list = ["front", "rear", "left", "right"]
    return render(request, "entry_form.html", {"position_list": position_list})


class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all().order_by("-timestamp")
    serializer_class = EntrySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head"]
    filter_backends = [filters.SearchFilter]
    search_fields = ['plate_number']

    def perform_create(self, serializer):
        area = Area.objects.first()
        plate_number = self.request.data.get("plate_number")
        no_plate = self.request.data.get("no_plate_number") == "true"

        if not no_plate and plate_number:
            vehicle = Vehicle.objects.create(
                plate_number=plate_number.upper().strip(),
                area=area
            )
        else:
            vehicle = None

        serializer.save(vehicle=vehicle, area=area)

    def get_queryset(self):
        vehicle_id = self.request.query_params.get("vehicle")
        qs = Entry.objects.select_related("vehicle").order_by("-timestamp")
        if vehicle_id:
            return qs.filter(vehicle_id=vehicle_id)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @action(detail=False, url_path="(?P<plate_number>[^/.]+)", methods=["get"])
    def get_by_plate(self, request, plate_number):
        try:
            entry = Entry.objects.filter(
                plate_number__iexact=plate_number, exit__isnull=True
            ).latest("timestamp")
            serializer = self.get_serializer(entry)
            return Response(serializer.data)
        except Entry.DoesNotExist:
            return Response(
                {"detail": "Mashina topilmadi yoki allaqachon chiqqan"},
                status=status.HTTP_404_NOT_FOUND,
            )


class EntryByPlateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, plate):
        try:
            entry = Entry.objects.filter(
                plate_number=plate, exitlog__isnull=True
            ).latest("timestamp")
        except Entry.DoesNotExist:
            return Response(
                {"error": "Kiritilgan raqamga mos kirish topilmadi."}, status=404
            )

        serializer = EntrySerializer(
            entry, context={"request": request}
        )  # <-- MUHIM QO‘SHIMCHA
        return Response(serializer.data)


class DRBReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Bu yerda DRB kameradan OCR o‘qish logikasi bo‘ladi
        # Hozircha test uchun random qiymat
        return Response({"plate_number": "30A123AA"})


# Camera In DRB view
class VehicleINANPRView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        ip_address = request.META.get("REMOTE_ADDR")
        if getattr(settings, "ALLOWED_CAMERA_IPS", None):
            if ip_address.split(",")[0] not in settings.ALLOWED_CAMERA_IPS:
                return Response({"error": "Unauthorized IP"}, status=401)

        xml_file = request.FILES.get('anpr.xml')
        if not xml_file:
            return Response({'error': 'XML file not found'}, status=400)

        try:
            xml_content = xml_file.read()
            root = ET.fromstring(xml_content)

            plate = root.findtext('.//licensePlate') or None
            detection_pic_node = root.find('.//pictureInfoList/pictureInfo/fileName')
            detection_pic_name = detection_pic_node.text if detection_pic_node is not None else None

        except ET.ParseError as e:
            return Response({'error': f'XML parse error: {str(e)}'}, status=400)

        detection_image = request.FILES.get(detection_pic_name) if detection_pic_name else None

        if not plate or not detection_image:
            return Response({'error': 'Plate number or detection image not found'}, status=400)

        if ExceptionalTransports.objects.filter(plate_number=plate).exists():
            return Response({"message": "This number is in the whitelist. Barrier opened."}, status=200)

        area = Area.objects.first()
        if not area:
            return Response({"error": "No Area found. Please configure Area first."}, status=400)

        yhxbb = YHXBB(area_id=area.area_id)
        try:
            api_response = yhxbb.car_entry(plate_number=plate, image_file=detection_image)
        except Exception as e:
            return Response({"error": f"YHXBB API call failed: {str(e)}"}, status=400)

        if api_response:
            area = Area.objects.first()
            vehicle = Vehicle.objects.create(area=area, plate_number=plate)
            plate_instance = Entry.objects.create(area=area, plate_number=plate, vehicle=vehicle,
                                                  photo_front=detection_image)
            return Response({"id": plate_instance.id, "status": True, "plate_number": plate_instance.plate_number,
                             "created_at": plate_instance.entry_time}, status=201)

        return Response({"error": "YHXBB API did not return success"}, status=400)


# Camera plate Out
class VehicleOutANPRView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        ip_address = request.META.get("REMOTE_ADDR")
        if getattr(settings, "ALLOWED_CAMERA_IPS", None):
            if ip_address.split(",")[0] not in settings.ALLOWED_CAMERA_IPS:
                return Response({"error": "Unauthorized IP"}, status=401)

        xml_file = request.FILES.get('anpr.xml')
        if not xml_file:
            return Response({'error': 'XML file not found'}, status=400)

        try:
            xml_content = xml_file.read()
            root = ET.fromstring(xml_content)

            plate = root.findtext('.//licensePlate') or None
            detection_pic_node = root.find('.//pictureInfoList/pictureInfo/fileName')
            detection_pic_name = detection_pic_node.text if detection_pic_node is not None else None

        except ET.ParseError as e:
            return Response({'error': f'XML parse error: {str(e)}'}, status=400)

        detection_image = request.FILES.get(detection_pic_name) if detection_pic_name else None

        if not plate or not detection_image:
            return Response({'error': 'Plate number or detection image not found'}, status=400)

        if ExceptionalTransports.objects.filter(plate_number=plate).exists():
            return Response({"message": "This number is in the whitelist. Barrier opened."}, status=200)

        plate_instance = Vehicle.objects.filter(plate_number=plate).first()
        if not plate_instance:
            return Response({"error": "Plate number not found in database"}, status=400)

        area = Area.objects.first()
        if not area:
            return Response({"error": "No Area found. Please configure Area first."}, status=400)

        yhxbb = YHXBB(area_id=area.area_id)
        try:
            api_response = yhxbb.car_exit(plate_number=plate, image_file=detection_image)
        except Exception as e:
            return Response({"error": f"YHXBB API call failed: {str(e)}"}, status=400)

        if api_response:
            entry_log = Entry.objects.filter(plate_number=plate_instance.plate_number)
            if entry_log:
                exit_log = ExitLog.objects.create(area=area, vehicle=plate_instance, entry=entry_log,
                                                  photo_front_exit=detection_image)
                return Response({"id": exit_log.id, "status": True, "plate_number": plate_instance.plate_number,
                                 "entry_time": entry_log.timestamp, "exit_time": exit_log.timestamp}, status=201)
            else:
                return Response({"message": "The car with this number did not enter the penalty area."}, status=400)
        return Response({"error": "YHXBB API did not return success"}, status=400)


class FullEntryExitStatisticsAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        try:
            date_range = request.query_params.get("date_range", "all_time")
            data_type = request.query_params.get("type", "all")

            today = now().date()

            if date_range == "daily":
                start_date = today
            elif date_range == "weekly":
                start_date = today - timedelta(days=7)
            elif date_range == "monthly":
                start_date = today - timedelta(days=30)
            elif date_range == "yearly":
                start_date = today - timedelta(days=365)
            else:
                start_date = None

            # Kirganlar
            entries = Entry.objects.all()
            if start_date:
                entries = entries.filter(timestamp__date__gte=start_date)

            # Chiqqanlar
            exits = ExitLog.objects.all()
            if start_date:
                exits = exits.filter(timestamp__date__gte=start_date)

            # Faqat kirgan yoki chiqqanlarni tanlash
            if data_type == "entries":
                exits = ExitLog.objects.none()
            elif data_type == "exits":
                entries = Entry.objects.none()

            entry_data = EntrySerializer(entries, many=True, context={"request": request}).data
            exit_data = ExitLogSerializer(exits, many=True, context={"request": request}).data

            return Response({
                "entries": entry_data,
                "exits": exit_data
            })

        except Exception as e:
            return Response({"error": f"Hisobotni olishda xatolik yuz berdi: {str(e)}"}, status=400)
