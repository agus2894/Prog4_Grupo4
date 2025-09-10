from django.shortcuts import render

def index(request):
    return render(request, 'tienda/index.html')

def login_view(request):
    return render(request, 'tienda/login.html')

def signup_view(request):
    return render(request, 'tienda/signup.html')

def logout_view(request):
    return render(request, 'tienda/logout.html')
