from django.urls import path
from . import views

app_name = 'presupuesto'

urlpatterns = [
    path('generar/', views.generar_presupuesto_desde_carrito, name='generar'),
    path('<int:presupuesto_id>/pdf/', views.descargar_pdf, name='descargar_pdf'),
    path('<int:presupuesto_id>/', views.ver_presupuesto, name='detalle'),
    path('', views.listar_presupuestos, name='lista'),
]
