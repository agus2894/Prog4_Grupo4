from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from tienda.models import Producto
import json


class UsuarioComportamiento(models.Model):
    """Rastrea el comportamiento del usuario para recomendaciones IA"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comportamientos")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    accion = models.CharField(max_length=20, choices=[
        ('view', 'Vio el producto'),
        ('cart', 'Agregó al carrito'),
        ('buy', 'Compró el producto'),
        ('search', 'Buscó producto similar'),
        ('compare', 'Comparó precios'),
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    tiempo_en_pagina = models.IntegerField(default=0)  # segundos
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['producto', 'accion']),
        ]


class RecomendacionIA(models.Model):
    """Almacena recomendaciones generadas por IA"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    producto_origen = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="recomendaciones_origen")
    producto_recomendado = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="recomendaciones_destino")
    score_confianza = models.FloatField()  # 0.0 a 1.0
    razon = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'producto_origen', 'producto_recomendado']


class ComparacionPrecios(models.Model):
    """Sistema de comparación de precios automático"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    precio_promedio_mercado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_minimo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_maximo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    es_oferta = models.BooleanField(default=False)
    porcentaje_ahorro = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def actualizar_comparacion(self):
        """Lógica IA para determinar si es una buena oferta"""
        productos_similares = Producto.objects.filter(
            marca=self.producto.marca,
            active=True
        ).exclude(id=self.producto.id)
        
        if productos_similares.exists():
            precios = [p.price for p in productos_similares]
            self.precio_promedio_mercado = sum(precios) / len(precios)
            self.precio_minimo = min(precios)
            self.precio_maximo = max(precios)
            
            # IA simple: si está 15% por debajo del promedio, es oferta
            if self.producto.price < self.precio_promedio_mercado * 0.85:
                self.es_oferta = True
                self.porcentaje_ahorro = ((self.precio_promedio_mercado - self.producto.price) / self.precio_promedio_mercado) * 100
            else:
                self.es_oferta = False
                self.porcentaje_ahorro = 0
        
        self.save()


class CarritoInteligente(models.Model):
    """Carrito con IA que recuerda productos y hace sugerencias"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)  # Para usuarios sin login
    productos_sugeridos = models.JSONField(default=list)  # IDs de productos sugeridos por IA
    productos_abandonados = models.JSONField(default=list)  # Productos que quitó del carrito
    score_intencion_compra = models.FloatField(default=0.0)  # 0.0 a 1.0
    ultimo_recordatorio = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calcular_score_intencion(self):
        """IA para calcular probabilidad de compra"""
        from django.utils import timezone
        import datetime
        
        score = 0.0
        
        # Más productos = mayor intención
        if self.user:
            items_count = self.user.carrito.items.count()
            score += min(items_count * 0.2, 0.6)
        
        # Tiempo desde última actividad
        tiempo_desde_update = timezone.now() - self.updated_at
        if tiempo_desde_update.days == 0:
            score += 0.3  # Actividad reciente
        elif tiempo_desde_update.days <= 2:
            score += 0.1
        
        # Productos abandonados indican indecisión
        score -= len(self.productos_abandonados) * 0.05
        
        self.score_intencion_compra = max(0.0, min(1.0, score))
        self.save()
        return self.score_intencion_compra


class TendenciaMercado(models.Model):
    """IA que analiza tendencias del mercado"""
    categoria = models.CharField(max_length=100)
    productos_trending = models.JSONField(default=list)  # IDs de productos en tendencia
    demanda_score = models.FloatField(default=0.0)
    precio_tendencia = models.CharField(max_length=20, choices=[
        ('subiendo', 'Precios Subiendo'),
        ('bajando', 'Precios Bajando'),
        ('estable', 'Precios Estables'),
    ], default='estable')
    fecha_analisis = models.DateTimeField(auto_now=True)
    
    @classmethod
    def analizar_tendencias(cls):
        """IA que analiza automáticamente las tendencias"""
        from django.db.models import Count, Avg
        from datetime import datetime, timedelta
        
        # Análisis de productos más vistos en última semana
        fecha_limite = datetime.now() - timedelta(days=7)
        productos_populares = UsuarioComportamiento.objects.filter(
            timestamp__gte=fecha_limite,
            accion__in=['view', 'cart', 'buy']
        ).values('producto').annotate(
            popularidad=Count('id')
        ).order_by('-popularidad')[:10]
        
        for categoria in ['Electrónicos', 'Ropa', 'Hogar', 'Deportes']:
            tendencia, created = cls.objects.get_or_create(categoria=categoria)
            tendencia.productos_trending = [p['producto'] for p in productos_populares]
            tendencia.save()