from django.db import models

# 🔥 OPCIONES DE DEPORTE
DEPORTE_CHOICES = [
    ('futbol', 'Fútbol'),
    ('baloncesto', 'Baloncesto'),
    ('tenis', 'Tenis'),
]

class Cancha(models.Model):
    nombre = models.CharField(max_length=100)
    deporte = models.CharField(max_length=20, choices=DEPORTE_CHOICES)
    precio_por_hora = models.DecimalField(max_digits=8, decimal_places=2)
    hora_apertura = models.TimeField()
    hora_cierre = models.TimeField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'cancha'