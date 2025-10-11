# usuarios/views.py
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import UserSerializer
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


def register(request):
    """Registro simple unificado"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada.')
            return redirect('tienda:index')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})
