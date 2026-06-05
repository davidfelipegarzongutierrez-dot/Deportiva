from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class RoleSecurityMiddleware(MiddlewareMixin):

    def process_request(self, request):

        path = request.path

        if not hasattr(request, "user"):
            return None

        if not request.user.is_authenticated:
            return None

        # RUTAS PERMITIDAS PARA USUARIOS NORMALES
        safe_user_paths = [
            '/usuarios/perfil/',
            '/usuarios/registro/',
        ]

        if any(path.startswith(p) for p in safe_user_paths):
            return None

        # BLOQUEO ADMIN
        admin_paths = [
            '/admin-panel/',
            '/canchas/crear/',
        ]

        for admin_path in admin_paths:
            if path.startswith(admin_path):
                if not request.user.is_superuser:
                    return redirect(reverse('home'))

        # BLOQUEO RESERVAS
        if '/reservas/crear/' in path:
            if not request.user.is_superuser:
                return redirect(reverse('home'))

        return None