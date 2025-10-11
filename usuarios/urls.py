# usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # API simple
    path('api/users/', views.UserListCreate.as_view(), name='user-list-create'),
    
    # Registro simple
    path('registro/', views.register, name='register'),
]
