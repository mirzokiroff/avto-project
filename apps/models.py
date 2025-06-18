from django.db import models





# Camera model
class Camera(models.Model):
    BARRIER_TYPE = [
        ('IN', 'Entrance'),
        ('OUT', 'Exit'),
    ]
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField(default=554)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=120)
    type = models.CharField(max_length=3, choices=BARRIER_TYPE, default=BARRIER_TYPE.IN)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"rtsp://{self.username}:{self.password}@{self.ip_address}:{self.port}/stream"


# Avto model
class Avto(models.Model):
    number = models.CharField(max_length=10)
    in_photo = models.FileField(upload_to="avto_in/")
    out_photo = models.FileField(upload_to="avto_out/", blank=True, null=True)
    status = models.BooleanField(default=True)
    time_entry = models.DateTimeField(auto_now_add=True)
    time_departure = models.DateTimeField(blank=True, null=True)

    @property
    def standing_time(self):
        if self.time_entry and self.time_departure:
            return self.time_departure - self.time_entry
        return None

    def __str__(self):
        return self.number


# Penalty area
class Area(models.Model):
    area_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.area_id
