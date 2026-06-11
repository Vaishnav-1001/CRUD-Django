from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.
class todo(models.Model):
    #makes a foreign key
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.item_name

class OTPRecord(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        expiration_time = self.created_at + timezone.timedelta(minutes=5)
        return timezone.now() > expiration_time

