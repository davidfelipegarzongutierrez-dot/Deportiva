from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cancha
from .forms import CanchaForm


@login_required
def home(request):
    return render(request, 'home.html')


# 🔥 LISTA CON FILTROS
@login_required
def lista_canchas(request):
    canchas = Cancha.objects.all()

    # 🔍 FILTROS
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


# 🔥 Crear cancha (solo admin)
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

    return render(request, 'canchas/crear.html', {'form': form})


# 🔥 Editar cancha (solo admin)
@login_required
def editar_cancha(request, cancha_id):
    if not request.user.is_superuser:
        return redirect('home')

    cancha = get_object_or_404(Cancha, id=cancha_id)

    if request.method == 'POST':
        form = CanchaForm(request.POST, request.FILES, instance=cancha)
        if form.is_valid():
            form.save()
            return redirect('lista_canchas')
    else:
        form = CanchaForm(instance=cancha)

    return render(request, 'canchas/editar.html', {'form': form})


# 🔥 Eliminar cancha (solo admin)
@login_required
def eliminar_cancha(request, cancha_id):
    if not request.user.is_superuser:
        return redirect('home')

    cancha = get_object_or_404(Cancha, id=cancha_id)

    if request.method == 'POST':
        cancha.delete()
        return redirect('lista_canchas')

    return render(request, 'canchas/eliminar.html', {'cancha': cancha})

# 🔥 GENERAR PDF DE CANCHAS
from django.http import HttpResponse
from reportlab.pdfgen import canvas


@login_required
def reporte_canchas_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_canchas.pdf"'

    p = canvas.Canvas(response)

    # 🔥 TÍTULO
    p.setFont("Helvetica", 14)
    p.drawString(100, 800, "Reporte de Canchas")

    # 🔽 OBTENER DATOS
    canchas = Cancha.objects.all()

    y = 760

    p.setFont("Helvetica", 10)

    for cancha in canchas:
        texto = f"{cancha.nombre} - {cancha.deporte} - ${cancha.precio_por_hora}"
        p.drawString(50, y, texto)
        y -= 20

        # 🔥 Evitar que se salga de la página
        if y < 50:
            p.showPage()
            y = 800

    p.save()

    return response