from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
import json
from datetime import datetime, timedelta
from django.db.models import Count, Q, Avg
from django.contrib.auth.models import User
from django.utils import timezone

from .models import UsuarioComportamiento, RecomendacionIA, ComparacionPrecios, CarritoInteligente, TendenciaMercado
from tienda.models import Producto


class InteligenciaArtificial:
    """Motor de IA para recomendaciones y análisis"""
    
    @staticmethod
    def obtener_recomendaciones(user, producto_actual=None, limit=6):
        """IA que genera recomendaciones personalizadas"""
        recomendaciones = []
        
        if not user.is_authenticated:
            # Para usuarios anónimos: productos más populares
            populares = Producto.objects.filter(active=True, stock__gt=0).annotate(
                popularidad=Count('usuariocomportamiento')
            ).order_by('-popularidad')[:limit]
            return populares
        
        # 1. Productos basados en historial de compras
        compras_pasadas = UsuarioComportamiento.objects.filter(
            user=user, accion='buy'
        ).values_list('producto', flat=True)
        
        if compras_pasadas:
            # Buscar productos similares por marca/categoría
            productos_similares = Producto.objects.filter(
                Q(marca__in=Producto.objects.filter(id__in=compras_pasadas).values_list('marca', flat=True)) |
                Q(seller__in=Producto.objects.filter(id__in=compras_pasadas).values_list('seller', flat=True))
            ).exclude(id__in=compras_pasadas).filter(active=True, stock__gt=0)[:3]
            recomendaciones.extend(productos_similares)
        
        # 2. Productos que otros usuarios compraron juntos
        if producto_actual:
            usuarios_similares = UsuarioComportamiento.objects.filter(
                producto=producto_actual, accion__in=['buy', 'cart']
            ).values_list('user', flat=True)
            
            productos_relacionados = UsuarioComportamiento.objects.filter(
                user__in=usuarios_similares, accion__in=['buy', 'cart']
            ).exclude(producto=producto_actual).values('producto').annotate(
                score=Count('id')
            ).order_by('-score')[:3]
            
            for p in productos_relacionados:
                producto = Producto.objects.get(id=p['producto'])
                if producto.active and producto.stock > 0:
                    recomendaciones.append(producto)
        
        # 3. Completar con productos trending
        trending = TendenciaMercado.analizar_tendencias()
        productos_trending = Producto.objects.filter(
            active=True, stock__gt=0
        ).exclude(id__in=[r.id for r in recomendaciones])[:limit-len(recomendaciones)]
        recomendaciones.extend(productos_trending)
        
        return recomendaciones[:limit]
    
    @staticmethod
    def analizar_precio_inteligente(producto):
        """IA que analiza si un precio es buena oferta"""
        comparacion, created = ComparacionPrecios.objects.get_or_create(
            producto=producto
        )
        comparacion.actualizar_comparacion()
        
        resultado = {
            'es_oferta': comparacion.es_oferta,
            'porcentaje_ahorro': comparacion.porcentaje_ahorro or 0,
            'precio_promedio': float(comparacion.precio_promedio_mercado or 0),
            'recomendacion': 'Excelente precio!' if comparacion.es_oferta else 'Precio regular'
        }
        
        if comparacion.porcentaje_ahorro and comparacion.porcentaje_ahorro > 25:
            resultado['recomendacion'] = '🔥 ¡SÚPER OFERTA! ¡No lo dejes pasar!'
        elif comparacion.porcentaje_ahorro and comparacion.porcentaje_ahorro > 15:
            resultado['recomendacion'] = '✨ Buen precio, recomendado'
        
        return resultado


@login_required
def obtener_recomendaciones_ajax(request):
    """API para obtener recomendaciones en tiempo real"""
    producto_id = request.GET.get('producto_id')
    producto_actual = None
    
    if producto_id:
        try:
            producto_actual = Producto.objects.get(id=producto_id)
            # Registrar que el usuario vio este producto
            UsuarioComportamiento.objects.create(
                user=request.user,
                producto=producto_actual,
                accion='view'
            )
        except Producto.DoesNotExist:
            pass
    
    recomendaciones = InteligenciaArtificial.obtener_recomendaciones(
        request.user, producto_actual
    )
    
    data = []
    for producto in recomendaciones:
        analisis_precio = InteligenciaArtificial.analizar_precio_inteligente(producto)
        data.append({
            'id': producto.id,
            'title': producto.title,
            'price': float(producto.price),
            'image_url': producto.image.url if producto.image else None,
            'marca': producto.marca,
            'stock': producto.stock,
            'analisis_precio': analisis_precio
        })
    
    return JsonResponse({'recomendaciones': data})


@csrf_exempt
def registrar_comportamiento(request):
    """Registra comportamiento del usuario para IA"""
    if request.method == 'POST':
        data = json.loads(request.body)
        
        if request.user.is_authenticated:
            try:
                producto = Producto.objects.get(id=data['producto_id'])
                UsuarioComportamiento.objects.create(
                    user=request.user,
                    producto=producto,
                    accion=data['accion'],
                    tiempo_en_pagina=data.get('tiempo', 0)
                )
                return JsonResponse({'status': 'success'})
            except:
                pass
    
    return JsonResponse({'status': 'error'})


def comparar_precios(request, producto_id):
    """Vista para comparación inteligente de precios"""
    try:
        producto = Producto.objects.get(id=producto_id)
        analisis = InteligenciaArtificial.analizar_precio_inteligente(producto)
        
        # Productos similares para comparar
        productos_similares = Producto.objects.filter(
            marca=producto.marca,
            active=True
        ).exclude(id=producto.id)[:5]
        
        comparaciones = []
        for p in productos_similares:
            analisis_similar = InteligenciaArtificial.analizar_precio_inteligente(p)
            comparaciones.append({
                'producto': p,
                'analisis': analisis_similar
            })
        
        context = {
            'producto': producto,
            'analisis_principal': analisis,
            'comparaciones': comparaciones,
        }
        
        return render(request, 'analytics/comparar_precios.html', context)
        
    except Producto.DoesNotExist:
        return render(request, '404.html')


@method_decorator(login_required, name='dispatch')
class DashboardIA(TemplateView):
    """Dashboard con análisis de IA"""
    template_name = 'analytics/dashboard_ia.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        
        # Recomendaciones personalizadas
        context['recomendaciones'] = InteligenciaArtificial.obtener_recomendaciones(user)
        
        # Análisis del carrito inteligente
        carrito_inteligente, created = CarritoInteligente.objects.get_or_create(usuario=user)
        context['carrito_inteligente'] = carrito_inteligente
        
        # Productos en oferta detectados por IA
        ofertas_ia = []
        comparaciones = ComparacionPrecios.objects.filter(es_oferta=True)[:6]
        for comp in comparaciones:
            ia = InteligenciaArtificial()
            analisis = ia.analizar_precio_inteligente(comp.producto)
            ofertas_ia.append({
                'producto': comp.producto,
                'analisis': analisis
            })
        context['ofertas_ia'] = ofertas_ia
        
        # Estadísticas del usuario
        comportamientos = UsuarioComportamiento.objects.filter(usuario=user)
        context['stats'] = {
            'productos_vistos': comportamientos.aggregate(total=Count('vistas'))['total'] or 0,
            'productos_comprados': comportamientos.filter(comprado=True).count(),
            'tiempo_total': comportamientos.aggregate(total=Sum('tiempo_total'))['total'] or 0,
        }
        
        return context


@require_POST
@csrf_exempt
@login_required
def registrar_comportamiento(request):
    """Vista AJAX para registrar comportamiento del usuario en tiempo real"""
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        accion = data.get('accion', 'view')
        tiempo = data.get('tiempo', 0)
        
        producto = get_object_or_404(Producto, id=producto_id)
        
        # Registrar o actualizar comportamiento
        comportamiento, created = UsuarioComportamiento.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults={
                'vistas': 1 if accion == 'view' else 0,
                'tiempo_total': tiempo,
                'clicks': 1 if accion in ['click', 'compare'] else 0,
                'agregado_carrito': accion == 'add_cart',
                'comprado': accion == 'buy'
            }
        )
        
        if not created:
            # Actualizar comportamiento existente
            if accion == 'view':
                comportamiento.vistas += 1
                comportamiento.tiempo_total += tiempo
            elif accion in ['click', 'compare']:
                comportamiento.clicks += 1
            elif accion == 'add_cart':
                comportamiento.agregado_carrito = True
            elif accion == 'buy':
                comportamiento.comprado = True
            
            comportamiento.save()
        
        # Actualizar carrito inteligente
        carrito, _ = CarritoInteligente.objects.get_or_create(
            usuario=request.user,
            defaults={'productos_analizados': 0, 'score_intencion_compra': 0.0}
        )
        
        # Recalcular score de intención de compra
        total_comportamientos = UsuarioComportamiento.objects.filter(usuario=request.user)
        score = 0.0
        
        for comp in total_comportamientos:
            # Algoritmo de scoring
            score += min(comp.vistas * 0.1, 0.5)  # Máximo 0.5 por vistas
            score += min(comp.tiempo_total * 0.01, 0.3)  # Máximo 0.3 por tiempo
            score += comp.clicks * 0.15  # 0.15 por click
            if comp.agregado_carrito:
                score += 0.25
            if comp.comprado:
                score += 0.4
        
        carrito.score_intencion_compra = min(score / max(total_comportamientos.count(), 1), 1.0)
        carrito.productos_analizados = total_comportamientos.count()
        carrito.save()
        
        return JsonResponse({
            'success': True,
            'score_actualizado': carrito.score_intencion_compra
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def comparar_precios(request, producto_id):
    """Vista para mostrar comparación detallada de precios"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Obtener o crear análisis de precios
    ia = InteligenciaArtificial()
    analisis = ia.analizar_precio_inteligente(producto, request.user if request.user.is_authenticated else None)
    
    # Productos similares (simulado - en producción usarías ML)
    productos_similares = Producto.objects.filter(
        categoria=producto.categoria
    ).exclude(id=producto.id)[:5]
    
    # Agregar scores de IA simulados
    for p in productos_similares:
        p.ia_score = random.uniform(6.0, 9.5)
    
    # Historial de análisis
    historial_analisis = ComparacionPrecios.objects.filter(
        producto=producto
    ).order_by('-fecha_analisis')[:10]
    
    context = {
        'producto': producto,
        'analisis': analisis,
        'productos_similares': productos_similares,
        'historial_analisis': historial_analisis,
    }
    
    return render(request, 'analytics/comparar_precios.html', context)