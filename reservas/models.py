from django.db import models
from decimal import Decimal
from usuarios.models import Usuario
from canchas.models import Cancha
class Reserva(models.Model):

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )

    cancha = models.ForeignKey(
        Cancha,
        on_delete=models.CASCADE
    )

    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    TIPO_RESERVA = [
        ('privada', 'Privada'),
        ('publica', 'Publica'),
    ]

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_RESERVA,
        default='privada'
    )

    capacidad = models.PositiveIntegerField(default=10)

    jugadores = models.ManyToManyField(
        Usuario,
        related_name='reservas',
        blank=True
    )

    creada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.cancha} - {self.fecha}"
    

    @property
    def costo_total(self):

        from datetime import datetime

        inicio = datetime.combine(
            self.fecha,
            self.hora_inicio
        )

        fin = datetime.combine(
            self.fecha,
            self.hora_fin
        )

        horas = (fin - inicio).total_seconds() / 3600

        return Decimal(str(horas)) * self.cancha.precio_por_hora


    @property
    def aporte_por_jugador(self):

        jugadores = self.jugadores.count()

        if jugadores == 0:
            return self.costo_total

        return self.costo_total / Decimal(jugadores)

    class Meta:
        db_table = 'reserva'

        # 🔐 evita duplicados básicos por lógica
        constraints = [
            models.UniqueConstraint(
                fields=['cancha', 'fecha', 'hora_inicio', 'hora_fin'],
                name='unique_reserva_slot'
            )
        ]