from django import forms
from .models import Cancha

class CanchaForm(forms.ModelForm):
    class Meta:
        model = Cancha
        fields = '__all__'

        widgets = {
            'precio_por_hora': forms.NumberInput(
                attrs={
                    'placeholder': 'Ej: 30000',
                    'min': '0'
                }
            ),

            'hora_apertura': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'step': 1800
                }
            ),

            'hora_cierre': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'step': 1800
                }
            ),

            'direccion': forms.TextInput(
                attrs={
                    'placeholder': 'Ej: Calle 45 # 12-34, Ciudad'
                }
            ),

            'latitud': forms.NumberInput(
                attrs={
                    'placeholder': 'Ej: 4.60971',
                    'step': 'any'
                }
            ),

            'longitud': forms.NumberInput(
                attrs={
                    'placeholder': 'Ej: -74.08175',
                    'step': 'any'
                }
            ),
        }