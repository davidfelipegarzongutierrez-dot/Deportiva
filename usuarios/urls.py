from django.urls import path

from .views import (
    registro,
    password_reset_demo,
    perfil,
    lista_usuarios,
    perfil_publico
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
]