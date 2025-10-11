# usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # API simple para usuarios
    path('api/users/', views.UserListCreate.as_view(), name='user-list-create'),
]
