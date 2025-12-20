from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Vous pouvez ajouter des champs personnalisés ici si nécessaire
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(choices=[("f",'F'),("m","M")],max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    status = models.CharField(choices=[('active', 'ACTIVE'), ('inactive', 'INACTIVE'), ('pending', 'PENDING')], max_length=20, default='active')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    

