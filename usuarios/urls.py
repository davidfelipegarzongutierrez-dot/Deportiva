from django.urls import path

from .views import (
    registro,
    password_reset_demo,
    perfil,
    lista_usuarios,
    perfil_publico,
    lista_usuarios_admin,
    editar_usuario_admin,
    eliminar_usuario_admin,
    enviar_solicitud,
    aceptar_solicitud,
    rechazar_solicitud,
    solicitudes_amistad
)

urlpatterns = [

    path(
        'registro/',
        registro,
        name='registro'
    ),

    path(
        'password-reset-demo/',
        password_reset_demo,
        name='password_reset_demo'
    ),

    path(
        'micuenta/',
        perfil,
        name='perfil'
    ),

    path(
        'buscar/',
        lista_usuarios,
        name='lista_usuarios'
    ),

    path(
        'perfil/<str:username>/',
        perfil_publico,
        name='perfil_publico'
    ),

    # =========================================
    # ADMINISTRACIÓN DE USUARIOS
    # =========================================
    path(
        'admin/usuarios/',
        lista_usuarios_admin,
        name='admin_usuarios'
    ),

    path(
        'admin/usuarios/editar/<int:usuario_id>/',
        editar_usuario_admin,
        name='editar_usuario_admin'
    ),

    path(
        'admin/usuarios/eliminar/<int:usuario_id>/',
        eliminar_usuario_admin,
        name='eliminar_usuario_admin'
    ),

    # =========================================
    # AMISTADES
    # =========================================
    path(
        'amistad/enviar/<str:username>/',
        enviar_solicitud,
        name='enviar_solicitud'
    ),

    path(
        'amistad/aceptar/<int:solicitud_id>/',
        aceptar_solicitud,
        name='aceptar_solicitud'
    ),

    path(
        'amistad/rechazar/<int:solicitud_id>/',
        rechazar_solicitud,
        name='rechazar_solicitud'
    ),

    path(
        'amistad/solicitudes/',
        solicitudes_amistad,
        name='solicitudes_amistad'
    ),
]