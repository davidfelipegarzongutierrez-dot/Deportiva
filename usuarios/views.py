from datetime import date
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.urls import reverse

from .forms import (
    UsuarioCreationForm,
    PerfilUsuarioForm
)
from canchas.models import DEPORTE_CHOICES
from reservas.models import Reserva

User = get_user_model()


# =========================================
# REGISTRO
# =========================================
def registro(request):

    if request.method == 'POST':

        form = UsuarioCreationForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('/accounts/login/')

        else:
            print(form.errors)

    else:

        form = UsuarioCreationForm()

    return render(
        request,
        'registration/registro.html',
        {
            'form': form
        }
    )


# =========================================
# RECUPERAR CONTRASEÑA
# =========================================
def password_reset_demo(request):

    reset_url = None

    if request.method == 'POST':

        form = PasswordResetForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data['email']

            user = User.objects.filter(
                email=email
            ).first()

            if user:

                uid = urlsafe_base64_encode(
                    force_bytes(user.pk)
                )

                token = (
                    default_token_generator.make_token(user)
                )

                reset_url = request.build_absolute_uri(
                    reverse(
                        'password_reset_confirm',
                        kwargs={
                            'uidb64': uid,
                            'token': token
                        }
                    )
                )

    else:

        form = PasswordResetForm()

    return render(
        request,
        'registration/password_reset_demo.html',
        {
            'form': form,
            'reset_url': reset_url
        }
    )


# =========================================
# PERFIL USUARIO
# =========================================
@login_required
def perfil(request):

    print("ENTRE A PERFIL")

    if request.method == 'POST':

        form = PerfilUsuarioForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            return redirect('perfil')

    else:

        form = PerfilUsuarioForm(
            instance=request.user
        )

    return render(
        request,
        'usuarios/perfil.html',
        {
            'form': form
        }
    )


# =========================================
# BUSCADOR / DIRECTORIO DE JUGADORES
# =========================================
@login_required
def lista_usuarios(request):

    deporte = request.GET.get('deporte')
    ciudad = request.GET.get('ciudad')

    usuarios = User.objects.exclude(id=request.user.id)

    if deporte:
        usuarios = usuarios.filter(deporte_favorito=deporte)

    if ciudad:
        usuarios = usuarios.filter(ciudad__icontains=ciudad)

    return render(
        request,
        'usuarios/lista_usuarios.html',
        {
            'usuarios': usuarios,
            'deportes': DEPORTE_CHOICES,
            'deporte_seleccionado': deporte,
            'ciudad_seleccionada': ciudad
        }
    )


# =========================================
# PERFIL PÚBLICO DE OTRO USUARIO
# =========================================
@login_required
def perfil_publico(request, username):

    if username == request.user.username:
        return redirect('perfil')

    target_user = get_object_or_404(User, username=username)

    hoy = date.today()

    # Mostrar únicamente reservas públicas y futuras del usuario organizador
    reservas_organizadas = Reserva.objects.filter(
        usuario=target_user,
        tipo='publica',
        fecha__gte=hoy
    ).order_by('fecha', 'hora_inicio')

    return render(
        request,
        'usuarios/perfil_publico.html',
        {
            'target_user': target_user,
            'reservas': reservas_organizadas
        }
    )