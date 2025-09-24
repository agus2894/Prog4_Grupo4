# tienda/views.py
from rest_framework import viewsets, permissions
from .models import Producto
from .serializers import ProductoSerializer

# API con DRF
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]

# Django
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import ProductoForm


# Decorador
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


# CRUD
@method_decorator([login_required, user_passes_test(staff_required)], name="dispatch")
class ProductoListView(ListView):
    model = Producto
    template_name = "tienda/dashboard_list.html"
    context_object_name = "productos"


@method_decorator([login_required, user_passes_test(staff_required)], name="dispatch")
class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "tienda/dashboard_form.html"
    success_url = reverse_lazy("tienda:dashboard_list")

    def form_valid(self, form):
        producto = form.save(commit=False)   # NO lo guardamos todavía
        producto.seller = self.request.user  # Asignamos el vendedor
        producto.save()                      # Ahora sí lo guardamos
        return super().form_valid(form)


@method_decorator([login_required, user_passes_test(staff_required)], name="dispatch")
class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "tienda/dashboard_form.html"
    success_url = reverse_lazy("tienda:dashboard_list")

    def form_valid(self, form):
        producto = form.save(commit=False)
        producto.seller = self.request.user  # Reasignamos por seguridad
        producto.save()
        return super().form_valid(form)


@method_decorator([login_required, user_passes_test(staff_required)], name="dispatch")
class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = "tienda/dashboard_confirm_delete.html"
    success_url = reverse_lazy("tienda:dashboard_list")


# Catálogo público
def tienda_index(request):
    productos = Producto.objects.all()
    return render(request, "tienda/index.html", {"productos": productos})


@login_required
@user_passes_test(staff_required)
def vendedor_dashboard(request):
    productos = Producto.objects.filter(seller=request.user)
    form = ProductoForm()
    return render(
        request,
        "tienda/vendedor_dashboard.html",
        {"productos": productos, "form": form},
    )
