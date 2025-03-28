from utils.models import BaseModel
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserSegment(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return str(self.name)


class ClientProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    segments = models.ManyToManyField(UserSegment, related_name="users", blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    last_notification_date = models.DateTimeField(null=True, blank=True)
