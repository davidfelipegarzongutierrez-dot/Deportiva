from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.urls import reverse

from .forms import (
    UsuarioCreationForm,
    PerfilUsuarioForm,
    UsuarioAdminForm
)
from canchas.models import DEPORTE_CHOICES
from reservas.models import Reserva
from .models import SolicitudAmistad

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

    solicitudes_recibidas = SolicitudAmistad.objects.filter(
        destinatario=request.user
    )

    return render(
        request,
        'usuarios/perfil.html',
        {
            'form': form,
            'solicitudes_recibidas': solicitudes_recibidas
        }
    )


# =========================================
# BUSCADOR / DIRECTORIO DE JUGADORES
# =========================================
@login_required
def lista_usuarios(request):

    deporte = request.GET.get('deporte')
    ciudad = request.GET.get('ciudad')

    usuarios = User.objects.exclude(
        id=request.user.id
    )

    if deporte:
        usuarios = usuarios.filter(
            deporte_favorito=deporte
        )

    if ciudad:
        usuarios = usuarios.filter(
            ciudad__icontains=ciudad
        )

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

    target_user = get_object_or_404(
        User,
        username=username
    )

    hoy = date.today()

    # =========================================
    # RESERVAS PÚBLICAS DEL USUARIO
    # =========================================
    reservas_organizadas = Reserva.objects.filter(
        usuario=target_user,
        tipo='publica',
        fecha__gte=hoy
    ).order_by(
        'fecha',
        'hora_inicio'
    )

    # =========================================
    # SISTEMA DE AMISTADES
    # =========================================
    es_amigo = request.user.amigos.filter(
        id=target_user.id
    ).exists()

    solicitud_pendiente = SolicitudAmistad.objects.filter(
        remitente=request.user,
        destinatario=target_user
    ).exists()

    return render(
        request,
        'usuarios/perfil_publico.html',
        {
            'target_user': target_user,
            'reservas': reservas_organizadas,
            'es_amigo': es_amigo,
            'solicitud_pendiente': solicitud_pendiente,
        }
    )

# =========================================
# ADMIN - LISTA USUARIOS
# =========================================
@login_required
def lista_usuarios_admin(request):

    if not request.user.is_superuser:
        return redirect('home')

    usuarios = User.objects.all().order_by('username')

    return render(
        request,
        'usuarios/admin_lista.html',
        {
            'usuarios': usuarios
        }
    )

# =========================================
# ADMIN - EDITAR USUARIO
# =========================================
@login_required
def editar_usuario_admin(request, usuario_id):

    if not request.user.is_superuser:
        return redirect('home')

    usuario = get_object_or_404(
        User,
        id=usuario_id
    )

    if request.method == 'POST':

        form = UsuarioAdminForm(
            request.POST,
            instance=usuario
        )

        if form.is_valid():

            usuario_editado = form.save(commit=False)

            # Evitar quitarse privilegios a sí mismo
            if (
                usuario == request.user
                and not usuario_editado.is_superuser
            ):

                messages.error(
                    request,
                    'No puedes quitarte privilegios de administrador.'
                )

                return redirect(
                    'editar_usuario_admin',
                    usuario_id=usuario.id
                )

            # Evitar quitar privilegios al último administrador
            if (
                usuario.is_superuser
                and not usuario_editado.is_superuser
            ):

                total_admins = User.objects.filter(
                    is_superuser=True
                ).count()

                if total_admins <= 1:

                    messages.error(
                        request,
                        'Debe existir al menos un administrador en el sistema.'
                    )

                    return redirect(
                        'editar_usuario_admin',
                        usuario_id=usuario.id
                    )

            usuario_editado.save()

            messages.success(
                request,
                'Usuario actualizado correctamente.'
            )

            return redirect('admin_usuarios')

    else:

        form = UsuarioAdminForm(
            instance=usuario
        )

    return render(
        request,
        'usuarios/editar_usuario.html',
        {
            'form': form,
            'usuario_obj': usuario
        }
    )

# =========================================
# ADMIN - ELIMINAR USUARIO
# =========================================
@login_required
def eliminar_usuario_admin(request, usuario_id):

    if not request.user.is_superuser:
        return redirect('home')

    usuario = get_object_or_404(
        User,
        id=usuario_id
    )

    if request.method == 'POST':

        if usuario == request.user:

            messages.error(
                request,
                'No puedes eliminar tu propia cuenta.'
            )

            return redirect('admin_usuarios')

        # Evitar eliminar el último administrador
        if usuario.is_superuser:

            total_admins = User.objects.filter(
                is_superuser=True
            ).count()

            if total_admins <= 1:

                messages.error(
                    request,
                    'Debe existir al menos un administrador en el sistema.'
                )

                return redirect('admin_usuarios')

        usuario.delete()

        messages.success(
            request,
            'Usuario eliminado correctamente.'
        )

        return redirect('admin_usuarios')

    return render(
        request,
        'usuarios/eliminar_usuario.html',
        {
            'usuario_obj': usuario
        }
    )

# =========================================
# ENVIAR SOLICITUD DE AMISTAD
# =========================================
@login_required
def enviar_solicitud(request, username):

    destinatario = get_object_or_404(
        User,
        username=username
    )

    if destinatario == request.user:

        messages.error(
            request,
            'No puedes enviarte una solicitud a ti mismo.'
        )

        return redirect(
            'perfil_publico',
            username=username
        )

    if request.user.amigos.filter(
        id=destinatario.id
    ).exists():

        messages.warning(
            request,
            'Ya son amigos.'
        )

        return redirect(
            'perfil_publico',
            username=username
        )

    # Evita solicitudes cruzadas
    if SolicitudAmistad.objects.filter(
        remitente=destinatario,
        destinatario=request.user
    ).exists():

        messages.info(
            request,
            'Ese usuario ya te envió una solicitud. Revísala en Solicitudes de amistad.'
        )

        return redirect(
            'perfil_publico',
            username=username
        )

    SolicitudAmistad.objects.get_or_create(
        remitente=request.user,
        destinatario=destinatario
    )

    messages.success(
        request,
        'Solicitud enviada correctamente.'
    )

    return redirect(
        'perfil_publico',
        username=username
    )


# =========================================
# ACEPTAR SOLICITUD
# =========================================
@login_required
def aceptar_solicitud(request, solicitud_id):

    solicitud = get_object_or_404(
        SolicitudAmistad,
        id=solicitud_id,
        destinatario=request.user
    )

    solicitud.remitente.amigos.add(
        request.user
    )

    solicitud.delete()

    messages.success(
        request,
        'Ahora son amigos.'
    )

    return redirect(
        'solicitudes_amistad'
    )


# =========================================
# RECHAZAR SOLICITUD
# =========================================
@login_required
def rechazar_solicitud(request, solicitud_id):

    solicitud = get_object_or_404(
        SolicitudAmistad,
        id=solicitud_id,
        destinatario=request.user
    )

    solicitud.delete()

    messages.info(
        request,
        'Solicitud rechazada.'
    )

    return redirect(
        'solicitudes_amistad'
    )

# =========================================
# SOLICITUDES PENDIENTES
# =========================================
@login_required
def solicitudes_amistad(request):

    solicitudes = SolicitudAmistad.objects.filter(
        destinatario=request.user
    ).select_related(
        'remitente'
    ).order_by(
        '-fecha'
    )

    return render(
        request,
        'usuarios/solicitudes_amistad.html',
        {
            'solicitudes': solicitudes,
            'amigos': request.user.amigos.all()
        }
    )