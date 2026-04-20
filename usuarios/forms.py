from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class UsuarioCreationForm(UserCreationForm):

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        help_text=""
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput,
        help_text=""
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

        help_texts = {
            'username': ""
        }