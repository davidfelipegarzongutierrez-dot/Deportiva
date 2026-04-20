from django import forms
from .models import Reserva
from datetime import date


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cancha', 'fecha', 'hora_inicio', 'hora_fin', 'capacidad', 'tipo']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        fecha = cleaned_data.get("fecha")
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")
        cancha = cleaned_data.get("cancha")

        # ❌ No fechas pasadas
        if fecha and fecha < date.today():
            raise forms.ValidationError("No puedes reservar en el pasado")

        # ❌ Hora inválida
        if hora_inicio and hora_fin:
            if hora_inicio >= hora_fin:
                raise forms.ValidationError("La hora de inicio debe ser menor a la hora final")

        # ❌ SOLAPAMIENTO (CLAVE)
        if fecha and hora_inicio and hora_fin and cancha:
            reservas_existentes = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio
            )

            if reservas_existentes.exists():
                raise forms.ValidationError("Esta cancha ya está reservada en ese horario. Intenta otro intervalo.")

        return cleaned_data