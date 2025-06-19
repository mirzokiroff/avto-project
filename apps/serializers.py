from rest_framework import serializers

from .models import Vehicle, EntryLog, ExitLog, FineStatus, CustomUser, ExceptionalTransports


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
