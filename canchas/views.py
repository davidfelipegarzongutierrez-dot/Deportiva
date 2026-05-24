from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import models

from reportlab.pdfgen import canvas

from .models import Cancha
from .forms import CanchaForm

from reservas.models import Reserva
from usuarios.models import Usuario


# =========================================
# HOME / DASHBOARD
# =========================================
@login_required
def home(request):

    total_canchas = Cancha.objects.count()

    total_reservas = Reserva.objects.count()

    reservas_disponibles = Reserva.objects.filter(
        jugadores__lt=models.F('capacidad')
    ).count()

    total_usuarios = Usuario.objects.count()

    # 🔥 ÚLTIMAS CANCHAS
    ultimas_canchas = Cancha.objects.order_by('-id')[:3]

    # 🔥 ÚLTIMAS RESERVAS
    ultimas_reservas = Reserva.objects.order_by('-id')[:5]

    context = {
        'total_canchas': total_canchas,
        'total_reservas': total_reservas,
        'reservas_disponibles': reservas_disponibles,
        'total_usuarios': total_usuarios,

        # 🔥 NUEVOS DATOS
        'ultimas_canchas': ultimas_canchas,
        'ultimas_reservas': ultimas_reservas,
    }

    return render(request, 'home.html', context)


# =========================================
# LISTA CANCHAS + FILTROS
# =========================================
@login_required
def lista_canchas(request):

    canchas = Cancha.objects.all()

    # FILTROS
    deporte = request.GET.get('deporte')
    precio_max = request.GET.get('precio_max')
    disponible = request.GET.get('disponible')

    if deporte:
        canchas = canchas.filter(deporte=deporte)

    if precio_max:
        canchas = canchas.filter(precio_por_hora__lte=precio_max)

    if disponible == 'on':
        canchas = canchas.filter(disponible=True)

    return render(request, 'canchas/lista_canchas.html', {
        'canchas': canchas
    })


# =========================================
# CREAR CANCHA
# =========================================
@login_required
def crear_cancha(request):

    if not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':

        form = CanchaForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('lista_canchas')

    else:
        form = CanchaForm()

    return render(request, 'canchas/crear.html', {
        'form': form
    })


# =========================================
# EDITAR CANCHA
# =========================================
@login_required
def editar_cancha(request, cancha_id):

    if not request.user.is_superuser:
        return redirect('home')

    cancha = get_object_or_404(Cancha, id=cancha_id)

    if request.method == 'POST':

        form = CanchaForm(
            request.POST,
            request.FILES,
            instance=cancha
        )

        if form.is_valid():
            form.save()
            return redirect('lista_canchas')

    else:
        form = CanchaForm(instance=cancha)

    return render(request, 'canchas/editar.html', {
        'form': form
    })


# =========================================
# ELIMINAR CANCHA
# =========================================
@login_required
def eliminar_cancha(request, cancha_id):

    if not request.user.is_superuser:
        return redirect('home')

    cancha = get_object_or_404(Cancha, id=cancha_id)

    if request.method == 'POST':
        cancha.delete()
        return redirect('lista_canchas')

    return render(request, 'canchas/eliminar.html', {
        'cancha': cancha
    })


# =========================================
# REPORTE PDF
# =========================================
@login_required
def reporte_canchas_pdf(request):

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = (
        'attachment; filename="reporte_canchas.pdf"'
    )

    p = canvas.Canvas(response)

    # TÍTULO
    p.setFont("Helvetica", 14)
    p.drawString(100, 800, "Reporte de Canchas")

    # DATOS
    canchas = Cancha.objects.all()

    y = 760

    p.setFont("Helvetica", 10)

    for cancha in canchas:

        texto = (
            f"{cancha.nombre} - "
            f"{cancha.deporte} - "
            f"${cancha.precio_por_hora}"
        )

        p.drawString(50, y, texto)

        y -= 20

        # NUEVA PÁGINA
        if y < 50:
            p.showPage()
            y = 800

    p.save()

    return response