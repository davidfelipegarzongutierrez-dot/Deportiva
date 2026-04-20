from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'usuario'