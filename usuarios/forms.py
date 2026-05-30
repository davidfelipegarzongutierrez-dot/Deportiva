from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class UsuarioCreationForm(UserCreationForm):

    email = forms.EmailField(
        label="Correo electrónico",
        required=True
    )

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
        fields = ('username', 'email', 'password1', 'password2')

        help_texts = {
            'username': "",
            'email': ""
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user
    
class PerfilUsuarioForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            'username',
            'email',
            'telefono',
            'foto_perfil',
            'biografia',
        ]

        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'foto_perfil': 'Foto de perfil',
            'biografia': 'Biografía',
        }

        widgets = {
            'biografia': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Cuéntanos algo sobre ti...'
                }
            )
        }