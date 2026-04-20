from django.urls import path
from .views import home, lista_canchas, crear_cancha, editar_cancha, eliminar_cancha, reporte_canchas_pdf

urlpatterns = [
    path('home/', home, name='home'),
    path('', lista_canchas, name='lista_canchas'),

    path('crear/', crear_cancha, name='crear_cancha'),
    path('editar/<int:cancha_id>/', editar_cancha, name='editar_cancha'),
    path('eliminar/<int:cancha_id>/', eliminar_cancha, name='eliminar_cancha'),
    path('reporte/pdf/', reporte_canchas_pdf, name='reporte_canchas_pdf'),
]