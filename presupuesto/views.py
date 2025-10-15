from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
from datetime import datetime
from tienda.models import Carrito
from .models import Presupuesto, PresupuestoItem


@login_required
def generar_presupuesto_desde_carrito(request):
    try:
        carrito = Carrito.objects.get(user=request.user)
        items_carrito = carrito.items.select_related('producto').all()
        
        if not items_carrito.exists():
            messages.warning(request, 'Tu carrito está vacío. Agrega productos antes de generar un presupuesto.')
            return redirect('tienda:ver_carrito')
        
        presupuesto = Presupuesto.objects.create(user=request.user)
        
        for item in items_carrito:
            PresupuestoItem.objects.create(
                presupuesto=presupuesto,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.price,
            )
        
        presupuesto.calcular_total()
        
        messages.success(request, f'Presupuesto #{presupuesto.id} generado exitosamente.')
        return redirect('presupuesto:descargar_pdf', presupuesto_id=presupuesto.id)
        
    except Carrito.DoesNotExist:
        messages.error(request, 'No se encontró tu carrito.')
        return redirect('tienda:index')


@login_required
def descargar_pdf(request, presupuesto_id):
    presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id, user=request.user)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    elementos = []
    
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'CustomTitle',
        parent=estilos['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        spaceAfter=30,
    )
    estilo_subtitulo = ParagraphStyle(
        'CustomSubtitle',
        parent=estilos['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    
    elementos.append(Paragraph("PRESUPUESTO", estilo_titulo))
    elementos.append(Paragraph(f"Presupuesto #{presupuesto.id}", estilo_subtitulo))
    elementos.append(Spacer(1, 0.3*inch))
    
    info_data = [
        ['Cliente:', request.user.get_full_name() or request.user.username],
        ['Email:', request.user.email],
        ['Fecha:', presupuesto.fecha_creacion.strftime('%d/%m/%Y %H:%M')],
        ['Estado:', presupuesto.get_estado_display()],
    ]
    
    tabla_info = Table(info_data, colWidths=[2*inch, 4*inch])
    tabla_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elementos.append(tabla_info)
    elementos.append(Spacer(1, 0.4*inch))
    
    elementos.append(Paragraph("Detalle de Productos", estilos['Heading2']))
    elementos.append(Spacer(1, 0.2*inch))
    
    datos_tabla = [['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']]
    
    for item in presupuesto.items.select_related('producto').all():
        datos_tabla.append([
            item.producto.title,
            str(item.cantidad),
            f"${item.precio_unitario:,.2f}",
            f"${item.subtotal:,.2f}",
        ])
    
    datos_tabla.append(['', '', 'TOTAL:', f"${presupuesto.total:,.2f}"])
    
    tabla_productos = Table(datos_tabla, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    tabla_productos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TEXTCOLOR', (0, 1), (-1, -2), colors.HexColor('#2c3e50')),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (2, -1), (2, -1), 'RIGHT'),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, -1), (-1, -1), 12),
        ('TOPPADDING', (0, -1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#3498db')),
    ]))
    elementos.append(tabla_productos)
    
    if presupuesto.notas:
        elementos.append(Spacer(1, 0.3*inch))
        elementos.append(Paragraph("Notas:", estilos['Heading3']))
        elementos.append(Paragraph(presupuesto.notas, estilos['Normal']))
    
    elementos.append(Spacer(1, 0.5*inch))
    estilo_footer = ParagraphStyle(
        'Footer',
        parent=estilos['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#95a5a6'),
        alignment=TA_CENTER,
    )
    elementos.append(Paragraph("Gracias por su preferencia", estilo_footer))
    elementos.append(Paragraph("Este presupuesto tiene validez de 30 días", estilo_footer))
    
    doc.build(elementos)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="presupuesto_{presupuesto.id}.pdf"'
    
    return response


@login_required
def ver_presupuesto(request, presupuesto_id):
    presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id, user=request.user)
    return render(request, 'presupuesto/detalle.html', {'presupuesto': presupuesto})


@login_required
def listar_presupuestos(request):
    presupuestos = Presupuesto.objects.filter(user=request.user).prefetch_related('items__producto')
    return render(request, 'presupuesto/lista.html', {'presupuestos': presupuestos})
