from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from tienda.views import ProductViewSet

# Swagger imports
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()
router.register(r"products", ProductViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Mercadito API",
        default_version="v1",
        description="API para manejar productos de Mercadito (compra, venta, trueque).",
        terms_of_service="https://www.google.com/policies/terms/",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),

    # Autenticación con allauth
    path("accounts/", include("allauth.urls")),

    # Swagger endpoints
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
