from datetime import date
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas

from .models import Reserva
from .forms import ReservaForm
from canchas.models import Cancha


# 🔹 Unirse a reserva pública
@login_required
def unirse_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.tipo != 'publica':
        messages.error(request, "Esta reserva no es pública")
        return redirect('reservas_disponibles')

    if request.user in reserva.jugadores.all():
        messages.warning(request, "Ya estás en esta reserva")
        return redirect('reservas_disponibles')

    if reserva.jugadores.count() >= reserva.capacidad:
        messages.error(request, "La reserva ya está llena")
        return redirect('reservas_disponibles')

    reserva.jugadores.add(request.user)
    messages.success(request, "Te uniste correctamente a la reserva")

    return redirect('reservas_disponibles')


# 🔹 Salirse de reserva
@login_required
def salir_reserva(request, reserva_id):
    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, id=reserva_id)

        if request.user in reserva.jugadores.all():
            reserva.jugadores.remove(request.user)
            messages.success(request, "Saliste de la reserva")

    return redirect('lista_reservas')


# 🔒 Mis reservas
@login_required
def lista_reservas(request):
    reservas = Reserva.objects.filter(jugadores=request.user)
    return render(request, 'reservas/lista.html', {'reservas': reservas})


# 🌐 Reservas disponibles
@login_required
def reservas_disponibles(request):
    reservas = Reserva.objects.filter(tipo='publica') \
        .exclude(jugadores=request.user)

    return render(request, 'reservas/disponibles.html', {'reservas': reservas})


# 👑 Crear reserva (ADMIN)
@login_required
def crear_reserva(request):
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.save()

            reserva.jugadores.add(request.user)

            messages.success(request, "Reserva creada correctamente")
            return redirect('lista_reservas')
    else:
        form = ReservaForm()

    return render(request, 'reservas/crear.html', {'form': form})


# 🔥 Crear reserva desde cancha
@login_required
def crear_reserva_desde_cancha(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)

            reserva.usuario = request.user
            reserva.cancha = cancha

            reserva.save()
            reserva.jugadores.add(request.user)

            messages.success(request, "Reserva creada desde la cancha")
            return redirect('lista_reservas')
    else:
        form = ReservaForm()

    return render(request, 'reservas/crear_desde_cancha.html', {
        'form': form,
        'cancha': cancha
    })


# 📄 PDF de mis reservas (MEJORADO)
@login_required
def reporte_reservas_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mis_reservas.pdf"'

    p = canvas.Canvas(response)

    reservas = Reserva.objects.filter(jugadores=request.user)

    # 🔥 Título mejorado
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "REPORTE DE MIS RESERVAS")

    y = 760
    p.setFont("Helvetica", 10)

    for reserva in reservas:
        texto = f"{reserva.cancha.nombre} | {reserva.fecha} | {reserva.hora_inicio} - {reserva.hora_fin}"
        p.drawString(50, y, texto)
        y -= 20

        if y < 50:
            p.showPage()
            y = 800

    # 🔥 total
    p.setFont("Helvetica", 10)
    p.drawString(50, y - 30, f"Total reservas: {reservas.count()}")

    p.save()

    return response