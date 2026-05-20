from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# 🔥 NUEVO
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('canchas/', include('canchas.urls')),
    path('reservas/', include('reservas.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    # 👇 ROOT
    path('', lambda request: redirect('/accounts/login/')),
]

# 🔥 MEDIA
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )