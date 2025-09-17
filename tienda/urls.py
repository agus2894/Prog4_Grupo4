from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet
from django.urls import path
from .views import tienda_index

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]

app_name = "tienda"

urlpatterns = [
    path("", tienda_index, name="index"),
]
