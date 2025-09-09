from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login

# Vista del inicio
def index(request):
    return render(request, 'tienda/index.html')

# Vista de login
def login_view(request):
    return render(request, 'tienda/login.html')

# Vista de registro (signup)
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():           # valida datos
            user = form.save()        # guarda en auth_user (PostgreSQL)
            login(request, user)      # inicia sesión automáticamente
            messages.success(request, "✅ Cuenta creada exitosamente")
            return redirect("shop")  # redirige al inicio
    else:
        form = UserCreationForm()      # formulario vacío
    return render(request, "tienda/signup.html", {"form": form})

# Vista de logout
def logout_view(request):
    return render(request, 'tienda/logout.html')

def shop(request):
    return render(request, "tienda/shop.html")

