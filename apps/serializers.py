from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Vehicle, EntryLog, ExitLog, FineStatus, CustomUser, ExceptionalTransports, Entry


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'is_admin', 'is_guard']


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'


class EntryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryLog
        fields = '__all__'


class ExitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExitLog
        fields = '__all__'


class FineStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FineStatus
        fields = '__all__'


class ExceptionalTransportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExceptionalTransports
        fields = '__all__'


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = 'admin' if self.user.is_superuser else 'user'
        return data


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ['id', 'plate_number', 'photo', 'is_manual', 'timestamp']


class CustomTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.contrib.auth import authenticate

        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Login yoki parol noto‘g‘ri.")

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'role': 'admin' if user.is_staff else 'user',
        }
