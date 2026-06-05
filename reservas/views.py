from datetime import date

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
        messages.error(request, "Método no permitido")
        return redirect('lista_reservas')

    reserva = get_object_or_404(
        Reserva,
        id=reserva_id,
        jugadores=request.user
    )

    # 🔐 el creador no puede abandonar su propia reserva
    if reserva.usuario == request.user:
        messages.error(
            request,
            "El creador de la reserva no puede abandonarla"
        )
        return redirect('lista_reservas')

    reserva.jugadores.remove(request.user)

    messages.success(
        request,
        "Saliste de la reserva correctamente"
    )

    return redirect('lista_reservas')


# =========================================
# LISTA DE RESERVAS (SEGURA POR ROL)
# =========================================
@login_required
def lista_reservas(request):

    hoy = date.today()

    base_query = Reserva.objects.filter(cancha__isnull=False)

    if request.user.is_superuser:

        reservas_activas = base_query.filter(
            fecha__gte=hoy
        ).order_by('fecha', 'hora_inicio')

        reservas_historial = base_query.filter(
            fecha__lt=hoy
        ).order_by('-fecha', '-hora_inicio')

    else:

        reservas_activas = base_query.filter(
            jugadores=request.user,
            fecha__gte=hoy
        ).order_by('fecha', 'hora_inicio')

        reservas_historial = base_query.filter(
            jugadores=request.user,
            fecha__lt=hoy
        ).order_by('-fecha', '-hora_inicio')

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

    return render(
        request,
        'reservas/disponibles.html',
        {
            'reservas': reservas
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
    )

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "REPORTE DE MIS RESERVAS")

    y = 760
    p.setFont("Helvetica", 10)

    for reserva in reservas:

        texto = (
            f"{reserva.cancha.nombre} | "
            f"{reserva.fecha} | "
            f"{reserva.hora_inicio} - "
            f"{reserva.hora_fin}"
        )

        p.drawString(50, y, texto)

        y -= 20

        if y < 50:
            p.showPage()
            y = 800

    p.drawString(
        50,
        y - 30,
        f"Total reservas: {reservas.count()}"
    )

    p.save()

    return response