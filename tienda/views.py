from rest_framework import viewsets
from rest_framework import permissions
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def redirect_dashboard(request):
    user = request.user
    if user.is_superuser:
        return redirect("/admin/")
    elif user.is_staff:
        return redirect("vendedor_dashboard")  # lo creamos abajo
    else:
        return redirect("tienda:index")  # catálogo público

from django.http import HttpResponse

@login_required
def vendedor_dashboard(request):
    if not request.user.is_staff:
        return HttpResponse("No tenés permisos para acceder aquí.", status=403)
    return HttpResponse(f"Bienvenido vendedor {request.user.username} (dashboard en construcción)")

from django.shortcuts import render

def tienda_index(request):
    productos = Product.objects.all()
    return render(request, "tienda/index.html", {"productos": productos})
