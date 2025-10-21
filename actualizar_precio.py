import os
from django.db.models import Producto
import django

def main():
    def mostrar_menu_principal():
        print("Menú Principal")
        print("v - Ver productos")
        print("m - Modificar precio")
        print("b - Buscar por marca")
        print("s - Salir")

    while True:
        mostrar_menu_principal()
        opcion = input("Opción: ")
        
        if opcion.lower() == 'v':
            mostrar_productos()
        elif opcion.lower() == 'm':
            modificar_precio()
        elif opcion.lower() == 'b':
            buscar_por_marca()
        elif opcion.lower() == 's':
            break

def mostrar_productos():
    productos = Producto.objects.all()
    for i, p in enumerate(productos, 1):
        print(f"  {i}. {p.title} | {p.marca} | ${p.price}")

def modificar_precio():
    mostrar_productos()
    seleccion = int(input("Número de producto: "))
    producto = Producto.objects.all()[seleccion-1]
    
    print(f"Producto: {producto.title}")
    print(f"Precio actual: ${producto.price}")
    
    nuevo_precio = float(input("Nuevo precio: $"))
    # Confirmar y guardar...

def buscar_por_marca():
    marca = input("Ingrese la marca a buscar: ")
    productos = Producto.objects.filter(marca__icontains=marca)
    if productos.exists():
        for i, p in enumerate(productos, 1):
            print(f"  {i}. {p.title} | {p.marca} | ${p.price}")
    else:
        print("No se encontraron productos con esa marca.")