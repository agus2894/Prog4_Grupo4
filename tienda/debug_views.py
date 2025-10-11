# Vista temporal para debugging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.middleware.csrf import get_token
from usuarios.models import Profile

@login_required
def debug_user(request):
    user = request.user
    csrf_token = get_token(request)
    
    # Si es POST, convertir en admin
    if request.method == 'POST' and request.POST.get('make_admin'):
        if hasattr(user, 'profile'):
            user.profile.is_admin = True
            user.profile.save()
            messages.success(request, '¡Ahora eres administrador!')
        else:
            Profile.objects.create(user=user, is_admin=True)
            messages.success(request, '¡Perfil creado y ahora eres administrador!')
        return redirect('tienda:debug_user')
    
    html = f"""
    <html>
    <head>
        <title>Debug Usuario</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
    <div class="container mt-4">
        <h2>🔍 Debug de Usuario</h2>
        
        <div class="card">
            <div class="card-body">
                <p><strong>Usuario:</strong> {user.username}</p>
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>is_staff:</strong> {user.is_staff}</p>
                <p><strong>is_superuser:</strong> {user.is_superuser}</p>
    """
    
    if hasattr(user, 'profile'):
        html += f"""
                <p><strong>Tiene Profile:</strong> ✅ Sí</p>
                <p><strong>is_admin:</strong> {user.profile.is_admin}</p>
        """
        
        if user.profile.is_admin:
            html += """
                <div class="alert alert-success">
                    ✅ ERES ADMINISTRADOR - Deberías ver el enlace "Admin" en el menú
                </div>
            """
        else:
            html += f"""
                <div class="alert alert-warning">
                    ⚠️ NO ERES ADMINISTRADOR
                </div>
                <form method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                    <button type="submit" name="make_admin" value="1" class="btn btn-primary">
                        🚀 Convertirme en Administrador
                    </button>
                </form>
            """
    else:
        html += f"""
                <p><strong>Tiene Profile:</strong> ❌ No (ERROR)</p>
                <div class="alert alert-danger">
                    🚨 ERROR: No tienes perfil creado
                </div>
                <form method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                    <button type="submit" name="make_admin" value="1" class="btn btn-success">
                        ✨ Crear Perfil de Administrador
                    </button>
                </form>
        """
    
    html += """
            </div>
        </div>
        
        <div class="mt-3">
            <a href="/" class="btn btn-secondary">🏠 Volver al inicio</a>
            <a href="/admin/" class="btn btn-info">⚙️ Admin Django</a>
            <a href="/tienda/dashboard/" class="btn btn-success">📊 Dashboard Productos</a>
        </div>
    </div>
    </body>
    </html>
    """
    
    return HttpResponse(html)