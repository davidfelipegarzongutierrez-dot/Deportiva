from django.contrib.auth.models import AbstractUser
from django.db import models
from canchas.models import DEPORTE_CHOICES

NIVEL_CHOICES = [
    ('principiante', 'Principiante'),
    ('intermedio', 'Intermedio'),
    ('avanzado', 'Avanzado'),
]

DISPONIBILIDAD_CHOICES = [
    ('semana_manana', 'Entre semana - Mañanas'),
    ('semana_tarde', 'Entre semana - Tardes'),
    ('semana_noche', 'Entre semana - Noches'),
    ('finde_manana', 'Fin de semana - Mañanas'),
    ('finde_tarde', 'Fin de semana - Tardes'),
    ('finde_noche', 'Fin de semana - Noches'),
    ('diaria', 'Todos los días'),
]

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

    # 🔥 CAMPOS DE PERFIL DEPORTIVO
    deporte_favorito = models.CharField(
        max_length=20,
        choices=DEPORTE_CHOICES,
        blank=True,
        null=True
    )

    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        blank=True,
        null=True
    )

    ciudad = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    posicion_juego = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    disponibilidad_habitual = models.CharField(
        max_length=30,
        choices=DISPONIBILIDAD_CHOICES,
        blank=True,
        null=True
    )

    biografia_deportiva = models.TextField(
        blank=True,
        null=True
    )

    amigos = models.ManyToManyField(
    'self',
    blank=True,
    symmetrical=True
    )



    def __str__(self):
        return self.username

    class Meta:
        db_table = 'usuario'


class SolicitudAmistad(models.Model):

    remitente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='solicitudes_enviadas'
    )

    destinatario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='solicitudes_recibidas'
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.remitente} -> "
            f"{self.destinatario}"
        )

    class Meta:
        db_table = 'solicitud_amistad'

        constraints = [
            models.UniqueConstraint(
                fields=[
                    'remitente',
                    'destinatario'
                ],
                name='solicitud_unica'
            )
        ]