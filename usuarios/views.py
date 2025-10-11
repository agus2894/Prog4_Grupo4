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


# usuarios/views.py
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import UserSerializer


class UserListCreate(generics.ListCreateAPIView):
    """API para listar y crear usuarios"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
