from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django.contrib import messages

from reportlab.pdfgen import canvas

from datetime import date

from .models import Cancha
from .forms import CanchaForm

from reservas.models import Reserva
from usuarios.models import Usuario


# =========================================
# HOME / DASHBOARD
# =========================================
@login_required
def home(request):

    hoy = date.today()

    total_canchas = Cancha.objects.count()

    # Solo reservas vigentes
    total_reservas = Reserva.objects.filter(
        fecha__gte=hoy
    ).count()

    # Solo reservas públicas vigentes
    reservas_disponibles = Reserva.objects.filter(
        tipo='publica',
        fecha__gte=hoy
    ).count()

    total_usuarios = Usuario.objects.count()

    # =========================
    # ESTADÍSTICAS PERSONALES
    # =========================

    mis_reservas = Reserva.objects.filter(
        jugadores=request.user,
        fecha__gte=hoy
    ).count()

    historial_reservas = Reserva.objects.filter(
        jugadores=request.user,
        fecha__lt=hoy
    ).count()

    # Últimas canchas
    ultimas_canchas = Cancha.objects.order_by('-id')[:3]

    # Últimas reservas vigentes
    if request.user.is_superuser:
        ultimas_reservas = Reserva.objects.filter(
            fecha__gte=hoy
        ).order_by(
            'fecha',
            'hora_inicio'
        )[:5]
    else:
        ultimas_reservas = Reserva.objects.filter(
            jugadores=request.user,
            fecha__gte=hoy
        ).order_by(
            'fecha',
            'hora_inicio'
        )[:5]

    context = {
        'total_canchas': total_canchas,
        'total_reservas': total_reservas,
        'reservas_disponibles': reservas_disponibles,
        'total_usuarios': total_usuarios,

        'mis_reservas': mis_reservas,
        'historial_reservas': historial_reservas,

        'ultimas_canchas': ultimas_canchas,
        'ultimas_reservas': ultimas_reservas,

        # ✅ fecha para dashboard
        'today': date.today().strftime("%d/%m/%Y"),
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

    cancha = get_object_or_404(
        Cancha,
        id=cancha_id
    )

    if request.method == 'POST':

        tiene_reservas = Reserva.objects.filter(
            cancha=cancha
        ).exists()

        if tiene_reservas:

            messages.error(
                request,
                "No se puede eliminar la cancha porque tiene reservas asociadas."
            )

            return redirect('lista_canchas')

        cancha.delete()

        messages.success(
            request,
            "Cancha eliminada correctamente."
        )

        return redirect('lista_canchas')

    return render(
        request,
        'canchas/eliminar.html',
        {
            'cancha': cancha
        }
    )


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

        # nueva página si se llena
        if y < 50:
            p.showPage()
            y = 800

    p.save()

    return response