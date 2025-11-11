from django.urls import path
from .views import noticias_view
from .views import (
    tienda_index,
    ProductoListView, ProductoCreateView,
    ProductoUpdateView, ProductoDeleteView,
    ver_carrito, agregar_al_carrito, actualizar_carrito,
    eliminar_del_carrito, vaciar_carrito, carrito_count,
    checkout, mis_pedidos, pedido_detalle,
    time_view,
)


app_name = "tienda"

urlpatterns = [
    path("", tienda_index, name="index"),
    
    path("dashboard/", ProductoListView.as_view(), name="dashboard_list"),
    path("dashboard/nuevo/", ProductoCreateView.as_view(), name="dashboard_create"),
    path("dashboard/<int:pk>/editar/", ProductoUpdateView.as_view(), name="dashboard_update"),
    path("dashboard/<int:pk>/eliminar/", ProductoDeleteView.as_view(), name="dashboard_delete"),

    path("carrito/", ver_carrito, name="ver_carrito"),
    path("carrito/agregar/<int:producto_id>/", agregar_al_carrito, name="agregar_al_carrito"),
    path("carrito/actualizar/<int:item_id>/", actualizar_carrito, name="actualizar_carrito"),
    path("carrito/eliminar/<int:item_id>/", eliminar_del_carrito, name="eliminar_del_carrito"),
    path("carrito/vaciar/", vaciar_carrito, name="vaciar_carrito"),
    path("api/carrito/count/", carrito_count, name="carrito_count"),
    
    path("checkout/", checkout, name="checkout"),
    path("pedidos/", mis_pedidos, name="mis_pedidos"),
    path("pedidos/<int:pedido_id>/", pedido_detalle, name="pedido_detalle"),
    path("tiempo/", time_view, name="tiempo"),
    path("noticias/", noticias_view, name="noticias"),
]
