from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers
from tienda.views import ProductoViewSet, redirect_dashboard
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# --- Swagger / Redoc ---
schema_view = get_schema_view(
    openapi.Info(
        title="Mi API",
        default_version='v1',
        description="Documentación de la API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# --- Router DRF ---
router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')

# --- URLs ---
urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API de productos
    path("api/", include(router.urls)),

    # Autenticación con allauth
    path("accounts/", include("allauth.urls")),

    # Dashboards
    path("redirect-dashboard/", redirect_dashboard, name="redirect_dashboard"),

    # Documentación API
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # Página de inicio
    path("", TemplateView.as_view(template_name="tienda/home.html"), name="home"),

    # URLs de la app tienda
    path("tienda/", include("tienda.urls")),
]
