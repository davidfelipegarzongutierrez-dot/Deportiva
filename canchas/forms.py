from django import forms
from .models import Cancha

class CanchaForm(forms.ModelForm):
    class Meta:
        model = Cancha
        fields = '__all__'

        widgets = {
            'hora_apertura': forms.TimeInput(attrs={'type': 'time'}),
            'hora_cierre': forms.TimeInput(attrs={'type': 'time'}),
        }