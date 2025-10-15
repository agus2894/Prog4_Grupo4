from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from tienda.views import ProductoViewSet, redirect_dashboard
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Mi API",
        default_version='v1',
        description="Documentación de la API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("accounts/", include("allauth.urls")),
    path("redirect-dashboard/", redirect_dashboard, name="redirect_dashboard"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("", TemplateView.as_view(template_name="tienda/home.html"), name="home"),
    path("tienda/", include("tienda.urls")),
    path("simple_chat/", include("simple_chat.urls")),
    path("presupuesto/", include("presupuesto.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
