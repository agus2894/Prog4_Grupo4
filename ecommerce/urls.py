from django.contrib import admin
from django.urls import path, include
from tienda import views as tienda_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Tienda (frontend)
    path('', tienda_views.index, name='index'),
    path('login/', tienda_views.login_view, name='login'),
    path('signup/', tienda_views.signup_view, name='signup'),
    path('logout/', tienda_views.logout_view, name='logout'),

    # API Usuarios
    path('api/', include('usuarios.urls')),
]
