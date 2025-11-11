import json
import os
from datetime import datetime, timedelta

import requests
from django.conf import settings
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
from django.core.cache import cache

from rest_framework import viewsets, permissions

from .models import Producto, Carrito, CarritoItem
from .serializers import ProductoSerializer
from .forms import ProductoForm
from telegram_bot.utils import enviar_pedido_telegram
from openai import OpenAI


def enviar_email_pedido(pedido, accion, request):
    try:
        configuracion_emails = {
            'creado': {
                'titulo': '¡Tu pedido ha sido confirmado!',
                'mensaje': 'Hemos recibido tu pedido y está siendo procesado.',
            },
            'procesando': {
                'titulo': 'Tu pedido está siendo procesado',
                'mensaje': 'Tu pedido está siendo preparado en nuestro almacén.',
            },
            'enviado': {
                'titulo': '¡Tu pedido está en camino!',
                'mensaje': 'Tu pedido ha sido enviado y está en camino.',
            },
            'entregado': {
                'titulo': '¡Pedido entregado exitosamente!',
                'mensaje': 'Esperamos que disfrutes tus productos.',
            },
            'cancelado': {
                'titulo': 'Tu pedido ha sido cancelado',
                'mensaje': 'Lamentamos informarte que tu pedido ha sido cancelado.',
            }
        }

        config = configuracion_emails.get(accion, configuracion_emails['creado'])
        context = {
            'pedido': pedido,
            'titulo_email': config['titulo'],
            'mensaje_email': config['mensaje'],
            'site_url': request.build_absolute_uri('/'),
        }

        html_content = render_to_string('emails/pedido_email.html', context)
        subject = f'[Mercadito] {config["titulo"]} - Pedido #{pedido.id}'
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[pedido.user.email],
        )
        email.content_subtype = 'html'
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

    def get_queryset(self):
        return Producto.objects.select_related('seller').filter(
            seller=self.request.user
        ).order_by('-created_at')


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
    productos_list = Producto.objects.select_related('seller').filter(active=True, stock__gt=0)

    search_query = request.GET.get('search', '')
    marca_filter = request.GET.get('marca', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    orden = request.GET.get('orden', 'recientes')

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

    marcas_disponibles = Producto.objects.filter(
        active=True, stock__gt=0
    ).values_list('marca', flat=True).distinct().order_by('marca')

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
    context = {'carrito': carrito, 'items': items}
    return render(request, 'tienda/carrito.html', context)


@login_required
def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id, active=True)
        cantidad = int(request.POST.get('cantidad', 1))
        if cantidad <= 0:
            messages.error(request, 'Cantidad inválida')
            return redirect('tienda:index')
        if cantidad > producto.stock:
            messages.error(request, f'Solo hay {producto.stock} disponibles')
            return redirect('tienda:index')

        with transaction.atomic():
            carrito = get_or_create_carrito(request.user)
            carrito.add_item(producto, cantidad)
            messages.success(request, f'{producto.title} agregado al carrito')

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
            messages.error(request, f'Solo hay {item.producto.stock} disponibles')
        else:
            item.cantidad = nueva_cantidad
            item.save()
            messages.success(request, 'Carrito actualizado')

    return redirect('tienda:ver_carrito')


@login_required
def eliminar_del_carrito(request, item_id):
    carrito = get_or_create_carrito(request.user)
    item = get_object_or_404(CarritoItem, id=item_id, carrito=carrito)
    item.delete()
    messages.success(request, 'Producto eliminado del carrito')
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
            return render(request, 'tienda/checkout.html', {'carrito': carrito, 'items': items})

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

                enviar_email_pedido(pedido, 'creado', request)
                enviar_pedido_telegram(request.user, pedido, 'creado')

                messages.success(request, f'¡Pedido #{pedido.id} creado exitosamente!')
                return redirect('tienda:pedido_detalle', pedido_id=pedido.id)

        except Exception:
            messages.error(request, 'Error al procesar el pedido')
            return redirect('tienda:ver_carrito')

    return render(request, 'tienda/checkout.html', {'carrito': carrito, 'items': items})


@login_required
def mis_pedidos(request):
    from .models import Pedido
    pedidos = Pedido.objects.filter(user=request.user).prefetch_related(
        'items__producto__seller'
    ).select_related('user').order_by('-fecha_pedido')
    return render(request, 'tienda/mis_pedidos.html', {'pedidos': pedidos})


@login_required
def pedido_detalle(request, pedido_id):
    from .models import Pedido
    pedido = get_object_or_404(Pedido, id=pedido_id, user=request.user)
    items = pedido.items.select_related('producto').all()
    return render(request, 'tienda/pedido_detalle.html', {'pedido': pedido, 'items': items})


# ---------- CLIMA, MAREAS Y NOTICIAS ----------

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
WORLD_TIDES_API_KEY = os.getenv('WORLD_TIDES_API_KEY')
MOON_API_KEY = os.getenv('MOON_API_KEY')

COASTS_RIVERS = [
    {"name": "Mar del Plata", "lat": -38.005, "lon": -57.5426},
    {"name": "Puerto Madryn", "lat": -42.7699, "lon": -65.0382},
    {"name": "Villa Gesell", "lat": -37.264, "lon": -56.97},
    {"name": "Mar de Ajó", "lat": -36.46, "lon": -56.735},
    {"name": "San Bernardo", "lat": -36.63, "lon": -56.722},
    {"name": "Río Paraná - Rosario", "lat": -32.9468, "lon": -60.6393},
    {"name": "Río Uruguay - Colón", "lat": -32.203, "lon": -58.17},
    {"name": "Río de la Plata - Buenos Aires", "lat": -34.6037, "lon": -58.3816},
]


def time_view(request):
    selected = request.GET.get("lugar", "Mar del Plata")
    lugar = next((c for c in COASTS_RIVERS if c["name"] == selected), COASTS_RIVERS[0])
    lat, lon = lugar["lat"], lugar["lon"]

    data = {
        "mareas": [],
        "viento": {},
        "clima": "",
        "temperatura": 0,
        "luna": "No disponible",
        "mejor_horario": "No disponible",
        "extremos": [],
        "error": None
    }

    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=es&appid={OPENWEATHER_API_KEY}"
        weather_resp = requests.get(weather_url, timeout=5)
        if weather_resp.status_code == 200:
            weather = weather_resp.json()
            data["viento"] = {
                "velocidad": weather.get("wind", {}).get("speed", 0),
                "direccion": weather.get("wind", {}).get("deg", 0)
            }
            data["clima"] = weather.get("weather", [{}])[0].get("description", "")
            data["temperatura"] = weather.get("main", {}).get("temp", 0)

        start_time = datetime.now()
        tides_url = f"https://www.worldtides.info/api/v3?heights&lat={lat}&lon={lon}&start={int(start_time.timestamp())}&length=86400&key={WORLD_TIDES_API_KEY}"
        tides_resp = requests.get(tides_url, timeout=10)
        if tides_resp.status_code == 200:
            tides = tides_resp.json()
            data["mareas"] = tides.get("heights", [])[:10]
            data["extremos"] = tides.get("extremes", [])[:10]

        moon_url = f"https://api.ipgeolocation.io/astronomy?apiKey={MOON_API_KEY}&lat={lat}&long={lon}"
        moon_resp = requests.get(moon_url, timeout=5)
        if moon_resp.status_code == 200:
            moon_data = moon_resp.json()
            fases = {
                "NEW_MOON": "Luna Nueva 🌑",
                "WAXING_CRESCENT": "Luna Creciente 🌒",
                "FIRST_QUARTER": "Cuarto Creciente 🌓",
                "WAXING_GIBBOUS": "Gibosa Creciente 🌔",
                "FULL_MOON": "Luna Llena 🌕",
                "WANING_GIBBOUS": "Gibosa Menguante 🌖",
                "LAST_QUARTER": "Cuarto Menguante 🌗",
                "WANING_CRESCENT": "Luna Menguante 🌘",
            }
            data["luna"] = fases.get(moon_data.get("moon_phase"), "No disponible")

    except Exception as e:
        data["error"] = str(e)

    context = {
        "lugar": lugar,
        "ciudad": selected,
        "fecha": datetime.now(),
        "data": data,
        "coasts_rivers": COASTS_RIVERS,
        "mareas_json": json.dumps(data["mareas"]),
    }

    return render(request, "tienda/tiempo.html", context)


def noticias_view(request):
    noticias = cache.get('noticias_pesca')
    if noticias:
        return render(request, "tienda/noticias.html", {"data": noticias})

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Escribe 5 noticias recientes de pesca en Argentina en JSON con title, summary, date y url"}],
            max_tokens=500
        )
        text = response.choices[0].message.content
        noticias = json.loads(text)
        cache.set('noticias_pesca', noticias, timeout=18000)
    except Exception:
        noticias = []

    return render(request, "tienda/noticias.html", {"data": noticias})
