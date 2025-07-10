from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.utils.validators import validate_phone_number
from config import settings


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("Yaratilgan vaqti"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yangilangan vaqti"), auto_now=True)

    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Foydalanuvchi nomi kiritilishi kerak!")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)


class CustomUser(AbstractUser, TimeStampedModel):
    full_name = models.CharField(_("To'liq ism"), max_length=100)
    phone = models.CharField(_("Telefon raqam"), max_length=13, validators=[validate_phone_number], unique=True)

    is_admin = models.BooleanField(_("Adminmi?"), default=False)
    is_guard = models.BooleanField(_("Xodimmi?"), default=False)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.phone


class Vehicle(TimeStampedModel):
    plate_number = models.CharField(_("Davlat raqami"), max_length=20, unique=True)
    owner_name = models.CharField(_("Egasining ismi"), max_length=255, blank=True)

    def __str__(self):
        return self.plate_number


class Camera(TimeStampedModel):
    BARRIER_TYPE = [
        ('IN', 'Kiruvchi'),
        ('OUT', 'Chiquvchi'),
    ]
    name = models.CharField(_("Nomi"), max_length=100)
    ip_address = models.GenericIPAddressField(_("IP manzili"))
    port = models.IntegerField(default=554)
    username = models.CharField(_("Kamera login"), max_length=50)
    password = models.CharField(_("Kamera parol"), max_length=120)
    type = models.CharField(_("Turi"), max_length=3, choices=BARRIER_TYPE)
    is_active = models.BooleanField(_("Faolligi"), default=True)
    created_at = models.DateTimeField(_("Yaratilgan"), auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.type}"


class EntryLog(TimeStampedModel):
    vehicle = models.ForeignKey("Vehicle", on_delete=models.CASCADE)
    photo = models.ImageField(_("Kirish rasmi"), upload_to='entry_photos/')
    entry_time = models.DateTimeField(_("Kirish vaqti"), default=timezone.now)
    is_manual = models.BooleanField(_("Qo'lda kiritilganmi?"), default=False)
    entry_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle.plate_number} kirgan - {self.entry_time}"


class ExitLog(TimeStampedModel):
    vehicle = models.ForeignKey("Vehicle", on_delete=models.CASCADE)
    photo = models.ImageField(_("Chiqish rasmi"), upload_to='exit_photos/')
    exit_time = models.DateTimeField(_("Chiqish vaqti"), default=timezone.now)
    paid_amount = models.DecimalField(_("To'langan summa"), max_digits=10, decimal_places=2)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    receipt = models.FileField(_("Kvitansiya fayli"), upload_to='receipts/', null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle.plate_number} chiqqan - {self.exit_time}"


class FineStatus(TimeStampedModel):
    vehicle = models.OneToOneField("Vehicle", on_delete=models.CASCADE)
    has_fine = models.BooleanField(_("Jarima mavjudmi?"), default=False)
    is_paid = models.BooleanField(_("To'langanmi?"), default=False)

    def __str__(self):
        return f"{self.vehicle.plate_number}: {'Bor' if self.has_fine else 'Yo‘q'}"


class Area(TimeStampedModel):
    area_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.area_id)


class ExceptionalTransports(TimeStampedModel):
    plate_number = models.CharField(_("Davlat raqami"), max_length=20, unique=True)
    owner_name = models.CharField(_("Egasining ismi"), max_length=255, blank=True)

    def __str__(self):
        return self.plate_number
