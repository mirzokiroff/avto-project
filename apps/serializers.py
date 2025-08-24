from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import (
    Vehicle,
    ExitLog,
    FineStatus,
    CustomUser,
    ExceptionalTransports,
    Entry, Area,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    photo_front_url = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = "__all__"

    def create(self, validated_data):
        if 'area' not in validated_data:
            validated_data['area'] = Area.objects.first().area_id
        return super().create(validated_data)

    def get_photo_front_url(self, obj):
        latest_entry = obj.entries.order_by("-timestamp").first()
        request = self.context.get("request")
        if latest_entry and latest_entry.photo_front:
            if request:
                return request.build_absolute_uri(latest_entry.photo_front.url)
            return latest_entry.photo_front.url  # Agar request bo‘lmasa faqat nisbiy URL
        return None


class ExitLogSerializer(serializers.ModelSerializer):
    vehicle_plate_number = serializers.CharField(
        source="vehicle.plate_number", read_only=True
    )
    entry_time = serializers.DateTimeField(source="entry.timestamp", read_only=True)
    entry = serializers.PrimaryKeyRelatedField(queryset=Entry.objects.all())
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())
    approved_by = UserSerializer(read_only=True)
    duration_display = serializers.SerializerMethodField()

    is_manual_entry = serializers.BooleanField(read_only=True)
    is_manual_exit = serializers.BooleanField()

    yard_fee = serializers.SerializerMethodField()

    photo_front_exit_url = serializers.SerializerMethodField()
    photo_rear_exit_url = serializers.SerializerMethodField()
    photo_left_exit_url = serializers.SerializerMethodField()
    photo_right_exit_url = serializers.SerializerMethodField()

    class Meta:
        model = ExitLog
        fields = '__all__'
        read_only_fields = ["timestamp", "total_minutes"]

    def get_yard_fee(self, obj):
        return obj.calculate_yard_fee()

    def get_duration_display(self, obj):
        minutes = obj.total_minutes or 0
        if minutes >= 60:
            return f"{minutes // 60} soat {minutes % 60} daqiqa"
        return f"{minutes} daqiqa"

    def get_photo_front_exit_url(self, obj):
        return obj.photo_front_exit.url if obj.photo_front_exit else None

    def get_photo_rear_exit_url(self, obj):
        return obj.photo_rear_exit.url if obj.photo_rear_exit else None

    def get_photo_left_exit_url(self, obj):
        return obj.photo_left_exit.url if obj.photo_left_exit else None

    def get_photo_right_exit_url(self, obj):
        return obj.photo_right_exit.url if obj.photo_right_exit else None


class FineStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FineStatus
        fields = "__all__"


class ExceptionalTransportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExceptionalTransports
        fields = "__all__"
        read_only_fields = ["id"]


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = "admin" if user.is_admin else "guard"
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["role"] = "admin" if self.user.is_admin else "guard"
        return data


class EntrySerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    is_exceptional = serializers.SerializerMethodField()

    photo_front_url = serializers.SerializerMethodField()
    photo_rear_url = serializers.SerializerMethodField()
    photo_left_url = serializers.SerializerMethodField()
    photo_right_url = serializers.SerializerMethodField()

    exitlog = ExitLogSerializer(read_only=True)

    class Meta:
        model = Entry
        fields = [
            "id",
            "vehicle",
            "plate_number",
            "no_plate_number",
            "photo_front",
            "photo_rear",
            "photo_left",
            "photo_right",
            "photo_front_url",
            "photo_rear_url",
            "photo_left_url",
            "photo_right_url",
            "is_manual",
            "is_exceptional",
            "timestamp",
            "exitlog",
        ]

    def get_is_exceptional(self, obj):
        plate = obj.vehicle.plate_number if obj.vehicle else obj.plate_number
        if plate:
            return ExceptionalTransports.objects.filter(
                plate_number__iexact=plate.strip().upper()
            ).exists()
        return False

    def get_photo_url(self, photo_field):
        request = self.context.get("request")
        if photo_field and hasattr(photo_field, "url"):
            return (
                request.build_absolute_uri(photo_field.url)
                if request else photo_field.url
            )
        return ""

    def get_photo_front_url(self, obj):
        return self.get_photo_url(obj.photo_front)

    def get_photo_rear_url(self, obj):
        return self.get_photo_url(obj.photo_rear)

    def get_photo_left_url(self, obj):
        return self.get_photo_url(obj.photo_left)

    def get_photo_right_url(self, obj):
        return self.get_photo_url(obj.photo_right)


class CustomTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.contrib.auth import authenticate

        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Login yoki parol noto‘g‘ri.")

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": "admin" if user.is_staff else "user",
        }
