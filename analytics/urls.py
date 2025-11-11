from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard-ia/', views.DashboardIA.as_view(), name='dashboard_ia'),
    path('api/recomendaciones/', views.obtener_recomendaciones_ajax, name='recomendaciones_ajax'),
    path('api/comportamiento/', views.registrar_comportamiento, name='registrar_comportamiento'),
    path('comparar-precios/<int:producto_id>/', views.comparar_precios, name='comparar_precios'),
]