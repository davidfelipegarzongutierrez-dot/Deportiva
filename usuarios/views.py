from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UsuarioCreationForm


def registro(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            print(form.errors)  # ayuda para debug
    else:
        form = UsuarioCreationForm()

    return render(request, 'registration/registro.html', {'form': form})