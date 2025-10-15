# tienda/views.py
from rest_framework import viewsets, permissions
from .models import Producto, Carrito, CarritoItem
from .serializers import ProductoSerializer

# API con DRF
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]

# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from .forms import ProductoForm

# Importar decoradores personalizados
from usuarios.decorators import role_required, vendedor_required, cliente_required, RoleRequiredMixin


# Decorador actualizado para roles
@login_required
def redirect_dashboard(request):
    user = request.user
    if hasattr(user, 'profile'):
        if user.profile.is_admin:
            return redirect("/admin/")
        elif user.profile.is_vendedor:
            return redirect("tienda:dashboard_list")
        else:
            return redirect("tienda:index")
    else:
        # Si no tiene perfil, crear uno y redirigir
        return redirect("tienda:index")


# CRUD con paginación y control de roles
class ProductoListView(RoleRequiredMixin, ListView):
    model = Producto
    template_name = "tienda/dashboard_list.html"
    context_object_name = "productos"
    paginate_by = 10  # 10 productos por página
    allowed_roles = ['admin', 'vendedor']

    def get_queryset(self):
        if self.request.user.profile.is_admin:
            return Producto.objects.all()  # Admin ve todos los productos
        else:
            return Producto.objects.filter(seller=self.request.user)  # Vendedor solo ve los suyos


class ProductoCreateView(RoleRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "tienda/dashboard_form.html"
    success_url = reverse_lazy("tienda:dashboard_list")
    allowed_roles = ['admin', 'vendedor']

    def form_valid(self, form):
        producto = form.save(commit=False)   # NO lo guardamos todavía
        producto.seller = self.request.user  # Asignamos el vendedor
        producto.save()                      # Ahora sí lo guardamos
        messages.success(self.request, f'Producto "{producto.title}" creado exitosamente.')
        return super().form_valid(form)


class ProductoUpdateView(RoleRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "tienda/dashboard_form.html"
    success_url = reverse_lazy("tienda:dashboard_list")
    allowed_roles = ['admin', 'vendedor']

    def get_queryset(self):
        if self.request.user.profile.is_admin:
            return Producto.objects.all()  # Admin puede editar cualquier producto
        else:
            return Producto.objects.filter(seller=self.request.user)  # Vendedor solo los suyos

    def form_valid(self, form):
        producto = form.save(commit=False)
        # Solo reasignar seller si es admin, vendedores mantienen la propiedad
        if not self.request.user.profile.is_admin:
            producto.seller = self.request.user
        producto.save()
        messages.success(self.request, f'Producto "{producto.title}" actualizado exitosamente.')
        return super().form_valid(form)


class ProductoDeleteView(RoleRequiredMixin, DeleteView):
    model = Producto
    template_name = "tienda/dashboard_confirm_delete.html"
    success_url = reverse_lazy("tienda:dashboard_list")
    allowed_roles = ['admin', 'vendedor']

    def get_queryset(self):
        if self.request.user.profile.is_admin:
            return Producto.objects.all()  # Admin puede eliminar cualquier producto
        else:
            return Producto.objects.filter(seller=self.request.user)  # Vendedor solo los suyos

    def delete(self, request, *args, **kwargs):
        producto = self.get_object()
        messages.success(request, f'Producto "{producto.title}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# Catálogo público con paginación
def tienda_index(request):
    productos_list = Producto.objects.filter(active=True, stock__gt=0)
    paginator = Paginator(productos_list, 12)  # 12 productos por página
    
    page = request.GET.get('page')
    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        productos = paginator.page(1)
    except EmptyPage:
        productos = paginator.page(paginator.num_pages)
    
    return render(request, "tienda/index.html", {"productos": productos})


# === FUNCIONALIDADES DEL CARRITO ===

def get_or_create_carrito(user):
    """Obtener o crear el carrito del usuario"""
    carrito, created = Carrito.objects.get_or_create(user=user)
    return carrito


@cliente_required
def ver_carrito(request):
    """Ver el contenido del carrito"""
    carrito = get_or_create_carrito(request.user)
    items = carrito.items.select_related('producto').all()
    
    context = {
        'carrito': carrito,
        'items': items,
        'total_items': carrito.total_items,
        'total_price': carrito.total_price,
    }
    return render(request, 'tienda/carrito.html', context)


@cliente_required
def agregar_al_carrito(request, producto_id):
    """Agregar un producto al carrito"""
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id, active=True)
        cantidad = int(request.POST.get('cantidad', 1))
        
        if cantidad <= 0:
            messages.error(request, 'La cantidad debe ser mayor a 0')
            return redirect('tienda:index')
        
        if cantidad > producto.stock:
            messages.error(request, f'Solo hay {producto.stock} unidades disponibles')
            return redirect('tienda:index')
        
        try:
            with transaction.atomic():
                carrito = get_or_create_carrito(request.user)
                carrito.add_item(producto, cantidad)
                messages.success(request, f'{producto.title} agregado al carrito')
        except Exception as e:
            messages.error(request, 'Error al agregar el producto al carrito')
    
    return redirect('tienda:index')


@cliente_required
def actualizar_carrito(request, item_id):
    """Actualizar la cantidad de un item del carrito"""
    if request.method == 'POST':
        carrito = get_or_create_carrito(request.user)
        item = get_object_or_404(CarritoItem, id=item_id, carrito=carrito)
        nueva_cantidad = int(request.POST.get('cantidad', 1))
        
        if nueva_cantidad <= 0:
            item.delete()
            messages.success(request, f'{item.producto.title} eliminado del carrito')
        elif nueva_cantidad > item.producto.stock:
            messages.error(request, f'Solo hay {item.producto.stock} unidades disponibles')
        else:
            item.cantidad = nueva_cantidad
            try:
                item.save()
                messages.success(request, 'Carrito actualizado')
            except Exception as e:
                messages.error(request, 'Error al actualizar el carrito')
    
    return redirect('tienda:ver_carrito')


@cliente_required
def eliminar_del_carrito(request, item_id):
    """Eliminar un producto del carrito"""
    carrito = get_or_create_carrito(request.user)
    item = get_object_or_404(CarritoItem, id=item_id, carrito=carrito)
    producto_title = item.producto.title
    item.delete()
    messages.success(request, f'{producto_title} eliminado del carrito')
    return redirect('tienda:ver_carrito')


@cliente_required
def vaciar_carrito(request):
    """Vaciar completamente el carrito"""
    if request.method == 'POST':
        carrito = get_or_create_carrito(request.user)
        carrito.clear()
        messages.success(request, 'Carrito vaciado')
    return redirect('tienda:ver_carrito')


@cliente_required
def carrito_count(request):
    """API endpoint para obtener el número de items en el carrito"""
    carrito = get_or_create_carrito(request.user)
    return JsonResponse({'count': carrito.total_items})


@vendedor_required
def vendedor_dashboard(request):
    productos = Producto.objects.filter(seller=request.user)
    form = ProductoForm()
    return render(
        request,
        "tienda/vendedor_dashboard.html",
        {"productos": productos, "form": form},
    )
