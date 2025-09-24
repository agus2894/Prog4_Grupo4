# tienda/urls.py
from django.urls import path
from .views import (
    tienda_index,
    ProductoListView, ProductoCreateView,
    ProductoUpdateView, ProductoDeleteView,
)

app_name = "tienda"

urlpatterns = [
    path("", tienda_index, name="index"),
    
    # Dashboard de vendedor (CRUD)
    path("dashboard/", ProductoListView.as_view(), name="dashboard_list"),
    path("dashboard/nuevo/", ProductoCreateView.as_view(), name="dashboard_create"),
    path("dashboard/<int:pk>/editar/", ProductoUpdateView.as_view(), name="dashboard_update"),
    path("dashboard/<int:pk>/eliminar/", ProductoDeleteView.as_view(), name="dashboard_delete"),

]
