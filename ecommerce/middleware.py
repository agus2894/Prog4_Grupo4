"""
Middleware personalizado para forzar el uso de localhost en desarrollo
"""
from django.conf import settings

class ForceLocalhostMiddleware:
    """
    Middleware que fuerza el uso de localhost en lugar de 127.0.0.1 para OAuth
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Modificar el host antes del procesamiento si es 127.0.0.1
        if settings.DEBUG and request.get_host().startswith('127.0.0.1:'):
            # Extraer el puerto
            port = request.get_host().split(':')[1] if ':' in request.get_host() else '8000'
            # Modificar el META para que Django use localhost
            request.META['HTTP_HOST'] = f'localhost:{port}'
            request.META['SERVER_NAME'] = 'localhost'
        
        response = self.get_response(request)
        return response