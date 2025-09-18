# tienda/urls.py
from django.urls import path
from .views import (
    tienda_index,
    ProductListView, ProductCreateView,
    ProductUpdateView, ProductDeleteView,
    vendedor_dashboard
)

app_name = "tienda"

urlpatterns = [
    path("", tienda_index, name="index"),
    
    # Dashboard de vendedor (CRUD)
    path("dashboard/", ProductListView.as_view(), name="dashboard_list"),
    path("dashboard/nuevo/", ProductCreateView.as_view(), name="dashboard_create"),
    path("dashboard/<int:pk>/editar/", ProductUpdateView.as_view(), name="dashboard_update"),
    path("dashboard/<int:pk>/eliminar/", ProductDeleteView.as_view(), name="dashboard_delete"),
    path("dashboard/vendedor/", vendedor_dashboard, name="vendedor_dashboard"),

]
