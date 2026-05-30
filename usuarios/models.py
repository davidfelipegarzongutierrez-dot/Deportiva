from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    foto_perfil = models.ImageField(
        upload_to='perfiles/',
        blank=True,
        null=True
    )

    biografia = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'usuario'