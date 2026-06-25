from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.lista_reservas,
        name='lista_reservas'
    ),

    path(
        'disponibles/',
        views.reservas_disponibles,
        name='reservas_disponibles'
    ),

    path(
        'unirse/<int:reserva_id>/',
        views.unirse_reserva,
        name='unirse_reserva'
    ),

    path(
        'salir/<int:reserva_id>/',
        views.salir_reserva,
        name='salir_reserva'
    ),

    # =========================================
    # CREAR RESERVAS
    # =========================================

    path(
        'crear/',
        views.crear_reserva,
        name='crear_reserva'
    ),

    path(
        'crear-desde-cancha/<int:cancha_id>/',
        views.crear_reserva_desde_cancha,
        name='crear_reserva_desde_cancha'
    ),

    # =========================================
    # REPORTES
    # =========================================

    path(
        'reporte/pdf/',
        views.reporte_reservas_pdf,
        name='reporte_reservas_pdf'
    ),

    path(
        'reporte/excel/',
        views.reporte_reservas_excel,
        name='reporte_reservas_excel'
    ),

    path(
        'reporte/txt/',
        views.reporte_reservas_txt,
        name='reporte_reservas_txt'
    ),

]