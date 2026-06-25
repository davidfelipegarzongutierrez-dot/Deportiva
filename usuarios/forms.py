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
            'telefono',
            'foto_perfil',
            'biografia',
            'deporte_favorito',
            'nivel',
            'ciudad',
            'posicion_juego',
            'disponibilidad_habitual',
            'biografia_deportiva',
        ]

        labels = {
            'username': 'Nombre de usuario',
            'telefono': 'Teléfono',
            'foto_perfil': 'Foto de perfil',
            'biografia': 'Sobre mí',
            'deporte_favorito': 'Deporte favorito',
            'nivel': 'Nivel de juego',
            'ciudad': 'Ciudad',
            'posicion_juego': 'Posición / Rol habitual',
            'disponibilidad_habitual': 'Disponibilidad habitual',
            'biografia_deportiva': 'Biografía deportiva',
        }

        widgets = {
            'biografia': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Cuéntanos algo sobre ti...'
                }
            ),
            'biografia_deportiva': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Cuéntanos tu experiencia, equipos o logros deportivos...'
                }
            ),
            'ciudad': forms.TextInput(
                attrs={
                    'placeholder': 'Ej: Bogotá, Medellín...'
                }
            ),
            'posicion_juego': forms.TextInput(
                attrs={
                    'placeholder': 'Ej: Delantero, Portero, Defensa, etc.'
                }
            ),
        }

class UsuarioAdminForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            'username',
            'email',
            'telefono',
            'ciudad',
            'deporte_favorito',
            'nivel',
            'is_superuser'
        ]

        labels = {
            'username': 'Usuario',
            'email': 'Correo',
            'telefono': 'Teléfono',
            'ciudad': 'Ciudad',
            'deporte_favorito': 'Deporte',
            'nivel': 'Nivel',
            'is_staff': 'Administrador'
        }