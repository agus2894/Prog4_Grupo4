# tienda/views.py
from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer

# API con DRF
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


# Django imports
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import ProductForm


# 🔹 Decorador: solo staff (vendedores/admin)
def staff_required(user):
    return user.is_staff


@login_required
def redirect_dashboard(request):
    user = request.user
    if user.is_superuser:
        return redirect("/admin/")
    elif user.is_staff:
        return redirect("tienda:dashboard_list")
    else:
        return redirect("tienda:index")


# ✅ Dashboard CRUD con vistas genéricas
@method_decorator([login_required, user_passes_test(staff_required)], name="dispatch")
class ProductListView(ListView):
    model = Product
    template_name = "tienda/dashboard_list.html"
    context_object_name = "productos"


@method_decorator([login_required, user_passes_test(staff_required)], name="dispatch")
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "tienda/dashboard_form.html"
    success_url = reverse_lazy("tienda:dashboard_list")


@method_decorator([login_required, user_passes_test(staff_required)], name="dispatch")
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "tienda/dashboard_form.html"
    success_url = reverse_lazy("tienda:dashboard_list")


@method_decorator([login_required, user_passes_test(staff_required)], name="dispatch")
class ProductDeleteView(DeleteView):
    model = Product
    template_name = "tienda/dashboard_confirm_delete.html"
    success_url = reverse_lazy("tienda:dashboard_list")


# Catálogo público
from django.shortcuts import render

def tienda_index(request):
    productos = Product.objects.all()
    return render(request, "tienda/index.html", {"productos": productos})

@login_required
@user_passes_test(staff_required)
def vendedor_dashboard(request):
    productos = Product.objects.filter(seller=request.user)
    form = ProductForm()
    return render(request, "tienda/vendedor_dashboard.html", {"productos": productos, "form": form})
