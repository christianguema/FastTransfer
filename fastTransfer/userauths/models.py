from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.contrib.auth.models import AbstractUser
from core.models import TimeStampMixin
from django.utils import timezone
from datetime import timedelta

class UserSatus(models.TextChoices):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"

class OTP(TimeStampMixin):
    code = models.CharField(max_length=10)
    is_expire = models.BooleanField()
    expire_at = models.DateTimeField()

    class Meta:
        verbose_name = "Otp"
        verbose_name_plural = "Otpt"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return self.code


class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(choices=[("f",'F'),("m","M")],max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    status = models.CharField(choices=UserSatus.choices, max_length=20, default='active')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    

