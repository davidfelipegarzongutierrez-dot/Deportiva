from django import forms
from .models import Reserva
from datetime import date, datetime, timedelta

class ReservaForm(forms.ModelForm):

    class Meta:
        model = Reserva
        fields = [
            'cancha',
            'fecha',
            'hora_inicio',
            'hora_fin',
            'capacidad',
            'tipo'
        ]

        widgets = {

            'fecha': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'hora_inicio': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'step': 1800,
                    'class': 'form-control'
                }
            ),

            'hora_fin': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'step': 1800,
                    'class': 'form-control'
                }
            ),

        }

    def clean(self):

        cleaned_data = super().clean()

        fecha = cleaned_data.get("fecha")
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")
        cancha = cleaned_data.get("cancha")

        # ❌ no pasado
        if fecha and fecha < date.today():
            raise forms.ValidationError("No puedes reservar en el pasado")

        # ❌ horario inválido
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise forms.ValidationError("Horario inválido")
        
        # =========================
        # DURACIÓN MÍNIMA 1 HORA
        # =========================
         
        if hora_inicio and hora_fin:

            inicio_dt = datetime.combine(date.today(), hora_inicio)
            fin_dt = datetime.combine(date.today(), hora_fin)

            duracion = fin_dt - inicio_dt

            if duracion < timedelta(hours=1):
                raise forms.ValidationError(
                    "La reserva debe durar mínimo 1 hora."
                )


        # =========================
        # RESPETAR HORARIO CANCHA
        # =========================

        if cancha:

            if hora_inicio < cancha.hora_apertura:
                raise forms.ValidationError(
                    f"La cancha abre a las {cancha.hora_apertura}"
                )

            if hora_fin > cancha.hora_cierre:
                raise forms.ValidationError(
                    f"La cancha cierra a las {cancha.hora_cierre}"
                )

        # =========================
        # SOLAPAMIENTO + DESCANSO 30 MIN
        # =========================

        if fecha and hora_inicio and hora_fin and cancha:

            nueva_inicio = datetime.combine(
                fecha,
                hora_inicio
            )

            nueva_fin = datetime.combine(
                fecha,
                hora_fin
            )

            reservas_existentes = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha
            )

            for reserva in reservas_existentes:

                reserva_inicio = datetime.combine(
                    fecha,
                    reserva.hora_inicio
                ) - timedelta(minutes=30)

                reserva_fin = datetime.combine(
                    fecha,
                    reserva.hora_fin
                ) + timedelta(minutes=30)

                if (
                    nueva_inicio < reserva_fin and
                    nueva_fin > reserva_inicio
                ):
                    raise forms.ValidationError(
                        "Debe existir un descanso mínimo de 30 minutos entre reservas."
            )

        return cleaned_data