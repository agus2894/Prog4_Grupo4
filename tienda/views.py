from rest_framework import viewsets, permissions
from .models import Producto, Carrito, CarritoItem
from .serializers import ProductoSerializer

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .forms import ProductoForm
from telegram_bot.utils import enviar_pedido_telegram


def enviar_email_pedido(pedido, accion, request):
    
    try:
        # Configurar título y mensaje según la acción
        configuracion_emails = {
            'creado': {
                'titulo': '¡Tu pedido ha sido confirmado!',
                'mensaje': 'Hemos recibido tu pedido y está siendo procesado. Te mantendremos informado sobre su estado.',
            },
            'procesando': {
                'titulo': 'Tu pedido está siendo procesado',
                'mensaje': 'Tu pedido está siendo preparado en nuestro almacén. Pronto será enviado.',
            },
            'enviado': {
                'titulo': '¡Tu pedido está en camino!',
                'mensaje': 'Tu pedido ha sido enviado y está en camino hacia tu dirección. Esperamos que lo recibas pronto.',
            },
            'entregado': {
                'titulo': '¡Pedido entregado exitosamente!',
                'mensaje': '¡Tu pedido ha sido entregado! Esperamos que disfrutes tus productos. Si tienes algún problema, contáctanos.',
            },
            'cancelado': {
                'titulo': 'Tu pedido ha sido cancelado',
                'mensaje': 'Lamentamos informarte que tu pedido ha sido cancelado. Si tienes preguntas, contáctanos.',
            }
        }
        
        config = configuracion_emails.get(accion, configuracion_emails['creado'])
        
        # Preparar contexto para el template
        context = {
            'pedido': pedido,
            'titulo_email': config['titulo'],
            'mensaje_email': config['mensaje'],
            'site_url': request.build_absolute_uri('/'),
        }
        
        # Renderizar template de email
        html_content = render_to_string('emails/pedido_email.html', context)
        
        # Crear email
        subject = f'[Mercadito] {config["titulo"]} - Pedido #{pedido.id}'
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[pedido.user.email],
        )
        email.content_subtype = 'html'
        
        # Enviar email
        email.send()
        return True
        
    except Exception as e:
        print(f"Error enviando email de pedido: {e}")
        return False


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]


def admin_required(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_admin


@login_required
def redirect_dashboard(request):
    if request.user.profile.is_admin:
        return redirect("/admin/")
    else:
        return redirect("tienda:index")


@method_decorator([login_required, user_passes_test(admin_required)], name="dispatch")
class ProductoListView(ListView):
    model = Producto
    template_name = "tienda/dashboard_list.html"
    context_object_name = "productos"
    paginate_by = 10


@method_decorator([login_required, user_passes_test(admin_required)], name="dispatch")
class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "tienda/dashboard_form.html"
    success_url = reverse_lazy("tienda:dashboard_list")

    def form_valid(self, form):
        producto = form.save(commit=False)
        producto.seller = self.request.user
        producto.save()
        messages.success(self.request, f'Producto "{producto.title}" creado.')
        return super().form_valid(form)


@method_decorator([login_required, user_passes_test(admin_required)], name="dispatch")
class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "tienda/dashboard_form.html"
    success_url = reverse_lazy("tienda:dashboard_list")

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado.')
        return super().form_valid(form)


@method_decorator([login_required, user_passes_test(admin_required)], name="dispatch")
class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = "tienda/dashboard_confirm_delete.html"
    success_url = reverse_lazy("tienda:dashboard_list")

    def delete(self, request, *args, **kwargs):
        producto = self.get_object()
        messages.success(request, f'Producto "{producto.title}" eliminado.')
        return super().delete(request, *args, **kwargs)


def tienda_index(request):
    productos_list = Producto.objects.filter(active=True, stock__gt=0)
    
    search_query = request.GET.get('search', '')
    marca_filter = request.GET.get('marca', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    orden = request.GET.get('orden', '')
    
    if search_query:
        from django.db.models import Q
        productos_list = productos_list.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(marca__icontains=search_query)
        )
    
    if marca_filter:
        productos_list = productos_list.filter(marca__iexact=marca_filter)
    
    if precio_min:
        try:
            productos_list = productos_list.filter(price__gte=float(precio_min))
        except ValueError:
            pass
    
    if precio_max:
        try:
            productos_list = productos_list.filter(price__lte=float(precio_max))
        except ValueError:
            pass
    
    if orden == 'precio_asc':
        productos_list = productos_list.order_by('price')
    elif orden == 'precio_desc':
        productos_list = productos_list.order_by('-price')
    elif orden == 'recientes':
        productos_list = productos_list.order_by('-created_at')
    elif orden == 'nombre':
        productos_list = productos_list.order_by('title')
    
    marcas_disponibles = Producto.objects.filter(active=True, stock__gt=0).values_list('marca', flat=True).distinct().order_by('marca')
    
    paginator = Paginator(productos_list, 12)
    page = request.GET.get('page')
    
    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        productos = paginator.page(1)
    except EmptyPage:
        productos = paginator.page(paginator.num_pages)
    
    context = {
        'productos': productos,
        'search_query': search_query,
        'marca_filter': marca_filter,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'orden': orden,
        'marcas_disponibles': marcas_disponibles,
        'total_resultados': paginator.count,
    }
    
    return render(request, "tienda/index.html", context)


def get_or_create_carrito(user):
    carrito, created = Carrito.objects.get_or_create(user=user)
    return carrito


@login_required
def ver_carrito(request):
    carrito = get_or_create_carrito(request.user)
    items = carrito.items.select_related('producto').all()
    
    context = {
        'carrito': carrito,
        'items': items,
        'total_items': carrito.total_items,
        'total_price': carrito.total_price,
    }
    return render(request, 'tienda/carrito.html', context)


@login_required
def agregar_al_carrito(request, producto_id):
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


@login_required
def actualizar_carrito(request, item_id):
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
            item.save()
            messages.success(request, 'Carrito actualizado')
    
    return redirect('tienda:ver_carrito')


@login_required
def eliminar_del_carrito(request, item_id):
    carrito = get_or_create_carrito(request.user)
    item = get_object_or_404(CarritoItem, id=item_id, carrito=carrito)
    producto_title = item.producto.title
    item.delete()
    messages.success(request, f'{producto_title} eliminado del carrito')
    return redirect('tienda:ver_carrito')


@login_required
def vaciar_carrito(request):
    if request.method == 'POST':
        carrito = get_or_create_carrito(request.user)
        carrito.clear()
        messages.success(request, 'Carrito vaciado')
    return redirect('tienda:ver_carrito')


@login_required
def carrito_count(request):
    carrito = get_or_create_carrito(request.user)
    return JsonResponse({'count': carrito.total_items})


@login_required
def checkout(request):
    carrito = get_or_create_carrito(request.user)
    items = carrito.items.select_related('producto').all()
    
    if not items.exists():
        messages.error(request, 'Tu carrito está vacío')
        return redirect('tienda:ver_carrito')
    
    if request.method == 'POST':
        direccion_envio = request.POST.get('direccion_envio', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        notas = request.POST.get('notas', '').strip()
        
        if not direccion_envio:
            messages.error(request, 'La dirección de envío es obligatoria')
            return render(request, 'tienda/checkout.html', {
                'carrito': carrito,
                'items': items,
                'total_price': carrito.total_price,
            })
        
        try:
            with transaction.atomic():
                for item in items:
                    if item.cantidad > item.producto.stock:
                        raise ValueError(f'Stock insuficiente para {item.producto.title}')
                
                from .models import Pedido, PedidoItem
                pedido = Pedido.objects.create(
                    user=request.user,
                    total=carrito.total_price,
                    direccion_envio=direccion_envio,
                    telefono=telefono,
                    notas=notas,
                    estado='pendiente'
                )
                
                for item in items:
                    PedidoItem.objects.create(
                        pedido=pedido,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio_unitario=item.producto.price
                    )
                    
                    item.producto.stock -= item.cantidad
                    item.producto.save()
                
                carrito.clear()
                
                # Enviar notificaciones
                email_enviado = enviar_email_pedido(pedido, 'creado', request)
                telegram_enviado = enviar_pedido_telegram(request.user, pedido, 'creado')
                
                # Mensajes de confirmación
                if email_enviado and telegram_enviado:
                    messages.success(request, f'¡Pedido #{pedido.id} creado exitosamente! Te hemos enviado confirmaciones por email y Telegram. 📧🤖')
                elif email_enviado:
                    messages.success(request, f'¡Pedido #{pedido.id} creado exitosamente! Te hemos enviado un email de confirmación. 📧')
                    if hasattr(request.user, 'profile') and request.user.profile.telegram_chat_id:
                        messages.info(request, 'No se pudo enviar por Telegram. Revisa tu vinculación.')
                elif telegram_enviado:
                    messages.success(request, f'¡Pedido #{pedido.id} creado exitosamente! Te hemos enviado confirmación por Telegram. 🤖')
                    messages.info(request, 'No pudimos enviar el email de confirmación.')
                else:
                    messages.success(request, f'¡Pedido #{pedido.id} creado exitosamente!')
                    messages.info(request, 'No pudimos enviar las notificaciones, pero tu pedido está confirmado.')
                
                return redirect('tienda:pedido_detalle', pedido_id=pedido.id)
                
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('tienda:ver_carrito')
        except Exception as e:
            messages.error(request, 'Error al procesar el pedido. Intenta nuevamente.')
            return redirect('tienda:ver_carrito')
    
    context = {
        'carrito': carrito,
        'items': items,
        'total_price': carrito.total_price,
    }
    return render(request, 'tienda/checkout.html', context)


@login_required
def mis_pedidos(request):
    from .models import Pedido
    pedidos = Pedido.objects.filter(user=request.user).prefetch_related('items__producto')
    return render(request, 'tienda/mis_pedidos.html', {'pedidos': pedidos})


@login_required
def pedido_detalle(request, pedido_id):
    from .models import Pedido
    pedido = get_object_or_404(Pedido, id=pedido_id, user=request.user)
    items = pedido.items.select_related('producto').all()
    
    context = {
        'pedido': pedido,
        'items': items,
    }
    return render(request, 'tienda/pedido_detalle.html', context)