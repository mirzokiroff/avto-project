from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.utils.validators import validate_phone_number


class TimeStampedModel(models.Model):
    entry_time = models.DateTimeField(_("Kirgan vaqti"), auto_now_add=True)
    exit_time = models.DateTimeField(_("Chiqqan vaqti"), auto_now=True)

    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Foydalanuvchi nomi kiritilishi kerak!")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractUser, TimeStampedModel, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(_("To'liq ism"), max_length=100)
    phone = models.CharField(
        _("Telefon raqam"),
        max_length=13,
        validators=[validate_phone_number],
        unique=True,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class Vehicle(TimeStampedModel):
    area = models.ForeignKey("apps.Area", on_delete=models.PROTECT)
    plate_number = models.CharField(
        _("Davlat raqami"), max_length=20, null=True, blank=False
    )
    no_plate_number = models.BooleanField(default=False)

    def __str__(self):
        return self.plate_number

    def save(self, *args, **kwargs):
        self.plate_number = self.plate_number.strip().upper()
        super().save(*args, **kwargs)


class Entry(TimeStampedModel):
    area = models.ForeignKey("apps.Area", on_delete=models.PROTECT)
    vehicle = models.ForeignKey(
        "apps.Vehicle",
        on_delete=models.CASCADE,
        related_name="entries",
        null=True,
        blank=True,
    )
    plate_number = models.CharField(max_length=30, null=True, blank=True)
    no_plate_number = models.BooleanField(default=False)
    yard_fee_paid = models.BooleanField(default=False)
    fine_paid = models.BooleanField(default=False)

    photo_front = models.ImageField(upload_to=f"entries/front/{timezone.localdate()}/", null=True, blank=True)
    photo_rear = models.ImageField(upload_to=f"entries/rear/{timezone.localdate()}/", null=True, blank=True)
    photo_left = models.ImageField(upload_to=f"entries/left/{timezone.localdate()}/", null=True, blank=True)
    photo_right = models.ImageField(upload_to=f"entries/right/{timezone.localdate()}/", null=True, blank=True)

    is_manual = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.vehicle:
            area = self.area

            if self.no_plate_number:
                temp_vehicle = Vehicle.objects.create(
                    plate_number="",
                    no_plate_number=True,
                    area=area
                )
                temp_vehicle.plate_number = f"DAVLAT RAQAMISIZ-{temp_vehicle.id}"
                temp_vehicle.save()

                self.plate_number = temp_vehicle.plate_number
                self.vehicle = temp_vehicle

            elif self.plate_number:
                self.plate_number = self.plate_number.strip().upper()
                vehicle, created = Vehicle.objects.get_or_create(
                    plate_number=self.plate_number,
                    defaults={"no_plate_number": False, "area": area}
                )
                self.vehicle = vehicle

        super().save(*args, **kwargs)

    def __str__(self):
        return self.plate_number or "Nomaʼlum transport"


class ExitLog(models.Model):
    area = models.ForeignKey("apps.Area", on_delete=models.PROTECT)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="exit")
    timestamp = models.DateTimeField(auto_now_add=True)
    is_manual_entry = models.BooleanField(default=False)
    is_manual_exit = models.BooleanField(default=False)
    photo_front_exit = models.ImageField(
        upload_to="exits/front/", null=True, blank=True
    )
    photo_rear_exit = models.ImageField(upload_to="exits/rear/", null=True, blank=True)
    photo_left_exit = models.ImageField(upload_to="exits/left/", null=True, blank=True)
    photo_right_exit = models.ImageField(
        upload_to="exits/right/", null=True, blank=True
    )
    yard_fee_paid = models.BooleanField(default=False)
    total_minutes = models.PositiveIntegerField(default=0)

    def calculate_yard_fee(self):
        entry_time = self.entry.timestamp
        exit_time = self.timestamp
        area = self.entry.vehicle.area

        if not area or not area.daily_fee:
            return 0

        duration = exit_time - entry_time
        total_days = int(duration.total_seconds() / 86400)
        if duration.total_seconds() % 86400 > 0:
            total_days += 1

        return total_days * area.daily_fee

    def __str__(self):
        return f"{self.vehicle.plate_number or 'Davlat raqamisiz'} chiqdi"


class FineStatus(TimeStampedModel):
    vehicle = models.OneToOneField("Vehicle", on_delete=models.CASCADE)
    has_fine = models.BooleanField(_("Jarima mavjudmi?"), default=False)
    is_paid = models.BooleanField(_("To'langanmi?"), default=False)

    def __str__(self):
        return f"{self.vehicle.plate_number}: {'Bor' if self.has_fine else 'Yo‘q'}"


class Area(TimeStampedModel):
    area_id = models.IntegerField(unique=True)
    daily_fee = models.PositiveIntegerField(default=10000, help_text="1 kunlik jarima maydon to‘lovi (so‘mda)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Maydon {self.area_id}"


class ExceptionalTransports(TimeStampedModel):
    plate_number = models.CharField(_("Davlat raqami"), max_length=20, unique=True)
    owner_name = models.CharField(
        _("Egasining ismi"), max_length=255, blank=True, null=True
    )
    phone_number = models.CharField(
        _("Telefon raqami"), max_length=20, blank=True, null=True
    )

    def __str__(self):
        return self.plate_number
