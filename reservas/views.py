from datetime import date

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from openpyxl import Workbook
from django.http import HttpResponse

from reportlab.pdfgen import canvas

from .models import Reserva
from .forms import ReservaForm
from canchas.models import Cancha



# =========================================
# UNIRSE A RESERVA PÚBLICA (SEGURA)
# =========================================
@login_required
def unirse_reserva(request, reserva_id):

    reserva = get_object_or_404(
        Reserva,
        id=reserva_id,
        tipo='publica'
    )

    # ❌ no reservas pasadas
    if reserva.fecha < date.today():
        messages.error(request, "No puedes unirte a una reserva pasada")
        return redirect('reservas_disponibles')

    # ❌ ya pertenece
    if reserva.jugadores.filter(id=request.user.id).exists():
        messages.warning(request, "Ya estás en esta reserva")
        return redirect('reservas_disponibles')

    # ❌ capacidad llena
    if reserva.jugadores.count() >= reserva.capacidad:
        messages.error(request, "La reserva ya está llena")
        return redirect('reservas_disponibles')

    reserva.jugadores.add(request.user)

    messages.success(request, "Te uniste correctamente a la reserva")

    return redirect('reservas_disponibles')


# =========================================
# SALIR DE RESERVA (SEGURA)
# =========================================
@login_required
def salir_reserva(request, reserva_id):

    if request.method != 'POST':
        messages.error(
            request,
            "Método no permitido"
        )
        return redirect('lista_reservas')

    reserva = get_object_or_404(
        Reserva,
        id=reserva_id,
        jugadores=request.user
    )

    # =========================
    # ORGANIZADOR
    # =========================
    if reserva.usuario == request.user:

        # Solo queda él
        if reserva.jugadores.count() == 1:

            reserva.delete()

            messages.success(
                request,
                "La reserva fue cancelada correctamente."
            )

            return redirect('lista_reservas')

        # Hay más participantes
        messages.error(
            request,
            "No puedes abandonar una reserva que tiene participantes."
        )

        return redirect('lista_reservas')

    # =========================
    # PARTICIPANTE NORMAL
    # =========================
    reserva.jugadores.remove(request.user)

    messages.success(
        request,
        "Saliste de la reserva correctamente."
    )

    return redirect('lista_reservas')


# =========================================
# LISTA DE RESERVAS (SEGURA POR ROL)
# =========================================
@login_required
def lista_reservas(request):

    hoy = date.today()

    base_query = Reserva.objects.filter(
        cancha__isnull=False
    )

    if request.user.is_superuser:

        reservas_activas = base_query.filter(
            fecha__gte=hoy
        ).order_by(
            'fecha',
            'hora_inicio'
        )

        reservas_historial = base_query.filter(
            fecha__lt=hoy
        ).order_by(
            '-fecha',
            '-hora_inicio'
        )

    else:

        reservas_activas = base_query.filter(
            jugadores=request.user,
            fecha__gte=hoy
        ).order_by(
            'fecha',
            'hora_inicio'
        )

        reservas_historial = base_query.filter(
            jugadores=request.user,
            fecha__lt=hoy
        ).order_by(
            '-fecha',
            '-hora_inicio'
        )

    # =========================================
    # CÁLCULO DE COSTOS
    # =========================================


    return render(
        request,
        'reservas/lista.html',
        {
            'reservas_activas': reservas_activas,
            'reservas_historial': reservas_historial,
        }
    )


# =========================================
# RESERVAS DISPONIBLES
# =========================================
@login_required
def reservas_disponibles(request):

    hoy = date.today()

    reservas = Reserva.objects.filter(
        tipo='publica',
        fecha__gte=hoy,
        cancha__isnull=False
    ).exclude(
        jugadores=request.user
    ).order_by(
        'fecha',
        'hora_inicio'
    )

    reservas_amigos = reservas.filter(
        usuario__in=request.user.amigos.all()
    )

    return render(
        request,
        'reservas/disponibles.html',
        {
            'reservas': reservas,
            'reservas_amigos': reservas_amigos
        }
    )


# =========================================
# CREAR RESERVA (ADMIN)
# =========================================
@login_required
def crear_reserva(request):

    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos")
        return redirect('home')

    if request.method == 'POST':

        form = ReservaForm(request.POST)

        if form.is_valid():

            reserva = form.save(commit=False)
            reserva.usuario = request.user

            # 🔐 evita duplicados reales
            existe = Reserva.objects.filter(
                cancha=reserva.cancha,
                fecha=reserva.fecha,
                hora_inicio=reserva.hora_inicio,
                hora_fin=reserva.hora_fin
            ).exists()

            if existe:
                messages.error(request, "Ya existe una reserva en ese horario")
                return redirect('crear_reserva')

            reserva.save()

            reserva.jugadores.add(request.user)

            messages.success(request, "Reserva creada correctamente")

            return redirect('lista_reservas')

    else:
        form = ReservaForm()

    return render(request, 'reservas/crear.html', {'form': form})


# =========================================
# CREAR RESERVA DESDE CANCHA
# =========================================
@login_required
def crear_reserva_desde_cancha(request, cancha_id):

    cancha = get_object_or_404(
        Cancha,
        id=cancha_id,
        disponible=True
    )

    if request.method == 'POST':

        form = ReservaForm(request.POST)

        if form.is_valid():

            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.cancha = cancha

            reserva.save()

            reserva.jugadores.add(request.user)

            messages.success(
                request,
                "Reserva creada desde la cancha"
            )

            return redirect('lista_reservas')

    else:
        form = ReservaForm()

    return render(
        request,
        'reservas/crear_desde_cancha.html',
        {
            'form': form,
            'cancha': cancha
        }
    )


# =========================================
# REPORTE PDF
# =========================================
@login_required
def reporte_reservas_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="mis_reservas.pdf"'
    )

    p = canvas.Canvas(response)

    reservas = Reserva.objects.filter(
        jugadores=request.user
    ).order_by('fecha', 'hora_inicio')

    # -------------------------
    # Encabezado
    # -------------------------

    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, 810, "REPORTE DE RESERVAS")

    p.setFont("Helvetica", 11)
    p.drawString(50, 790, f"Usuario: {request.user.username}")
    p.drawString(50, 775, f"Total de reservas: {reservas.count()}")

    y = 740

    for reserva in reservas:

        p.setFont("Helvetica-Bold", 11)
        p.drawString(
            50,
            y,
            reserva.cancha.nombre
        )

        y -= 15

        p.setFont("Helvetica", 10)

        p.drawString(
            60,
            y,
            f"Fecha: {reserva.fecha}"
        )

        y -= 15

        p.drawString(
            60,
            y,
            f"Horario: {reserva.hora_inicio} - {reserva.hora_fin}"
        )

        y -= 15

        p.drawString(
            60,
            y,
            f"Jugadores: {reserva.jugadores.count()} / {reserva.capacidad}"
        )

        y -= 15

        p.drawString(
            60,
            y,
            f"Costo: ${reserva.costo_total:,.0f}"
        )

        y -= 15

        p.drawString(
            60,
            y,
            f"Aporte por jugador: ${reserva.aporte_por_jugador:,.0f}"
        )

        y -= 25

        if y < 70:
            p.showPage()
            y = 800

    p.save()

    return response


# =========================================
# REPORTE EXCEL
# =========================================
@login_required
def reporte_reservas_excel(request):

    wb = Workbook()

    ws = wb.active
    ws.title = "Reservas"

    ws.append([
        "Cancha",
        "Fecha",
        "Hora inicio",
        "Hora fin",
        "Jugadores",
        "Costo",
        "Aporte por jugador"
    ])

    reservas = Reserva.objects.filter(
        jugadores=request.user
    ).order_by(
        'fecha',
        'hora_inicio'
    )

    for reserva in reservas:

        ws.append([
            reserva.cancha.nombre,
            str(reserva.fecha),
            str(reserva.hora_inicio),
            str(reserva.hora_fin),
            reserva.jugadores.count(),
            float(reserva.costo_total),
            float(reserva.aporte_por_jugador),
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = (
        'attachment; filename="mis_reservas.xlsx"'
    )

    wb.save(response)

    return response


# =========================================
# REPORTE TXT
# =========================================
@login_required
def reporte_reservas_txt(request):

    response = HttpResponse(
        content_type="text/plain"
    )

    response["Content-Disposition"] = (
        'attachment; filename="mis_reservas.txt"'
    )

    reservas = Reserva.objects.filter(
        jugadores=request.user
    ).order_by(
        'fecha',
        'hora_inicio'
    )

    response.write("========== REPORTE DE RESERVAS ==========\n\n")
    response.write(f"Usuario: {request.user.username}\n")
    response.write(f"Total reservas: {reservas.count()}\n\n")

    for reserva in reservas:

        response.write(
            f"Cancha: {reserva.cancha.nombre}\n"
        )

        response.write(
            f"Fecha: {reserva.fecha}\n"
        )

        response.write(
            f"Horario: {reserva.hora_inicio} - {reserva.hora_fin}\n"
        )

        response.write(
            f"Jugadores: {reserva.jugadores.count()} / {reserva.capacidad}\n"
        )

        response.write(
            f"Costo: ${reserva.costo_total:,.0f}\n"
        )

        response.write(
            f"Aporte por jugador: ${reserva.aporte_por_jugador:,.0f}\n"
        )

        response.write(
            "-" * 50 + "\n"
        )

    return response