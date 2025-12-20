from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.contrib.auth.models import AbstractUser
from core.models import TimeStampMixin

class UserSatut(models.TextChoices):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"

class OPT(TimeStampMixin):
    id_opt = ShortUUIDField(unique=True, length=2, max_length=5, alphabet="124")
    code = models.CharField(max_length=10)
    is_expire = models.BooleanField()
    expire_at = models.DateTimeField()

    class Meta:
        verbose_name = "Opt"
        verbose_name_plural = "Opt"


    def __str__(self):
        return self.code


class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(choices=[("f",'F'),("m","M")],max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    status = models.CharField(choices=UserSatut.choices, max_length=20, default='active')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    

