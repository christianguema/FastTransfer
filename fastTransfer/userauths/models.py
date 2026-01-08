from django.db import models
# from shortuuid.django_fields import ShortUUIDField
from django.contrib.auth.models import AbstractUser
from core.models import TimeStampMixin
from django.utils import timezone
# from datetime import timedelta

class UserSatus(models.TextChoices):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"

class OTP(TimeStampMixin):
    #Ajout d'une relation entre le model OTP et account owner pour la simplification de la gestion des verification du code OTP
    user_otp = models.ForeignKey(
        'User',
        on_delete=models.CASCADE
    )
    code = models.CharField(max_length=10)
    is_expire = models.BooleanField()
    expire_at = models.DateTimeField()

    class Meta:
        verbose_name = "Otp"
        verbose_name_plural = "Otp"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return self.code


class User(AbstractUser):
    # On définit les choix de rôles
    ADMIN = 'ADMIN'
    UTILISATEUR = 'USER'
    ROLE_CHOICES = [
        (ADMIN, 'Administrateur'),
        (UTILISATEUR, 'Utilisateur Standard'),
    ]

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(choices=[("f",'F'),("m","M")],max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    status = models.CharField(choices=UserSatus.choices, max_length=20, default='active')

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=UTILISATEUR)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def is_customer(self):
        return self.groups.filter(name="custumer").exists()

    @property
    def is_admin(self):
        return self.groups.filter(name="admins").exists()

    # Helper pour vérifier facilement dans les vues/templates
    def is_admin_custom(self):
        return self.role == self.ADMIN

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    

