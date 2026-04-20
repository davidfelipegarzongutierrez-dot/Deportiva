from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect  # 👈 IMPORTANTE

urlpatterns = [
    path('admin/', admin.site.urls),
    path('canchas/', include('canchas.urls')),
    path('reservas/', include('reservas.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    # 👇 ROOT SIEMPRE REDIRIGE AL LOGIN
    path('', lambda request: redirect('/accounts/login/')),
]