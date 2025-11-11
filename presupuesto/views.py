from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
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
from telegram_bot.utils import enviar_presupuesto_telegram


def enviar_email_presupuesto(presupuesto, request):
    """
    Envía un email con el presupuesto en PDF adjunto
    """
    try:
        # Generar PDF en memoria
        pdf_buffer = generar_pdf_presupuesto(presupuesto, request)
        
        # Preparar contexto para el template
        context = {
            'presupuesto': presupuesto,
            'site_url': request.build_absolute_uri('/'),
        }
        
        # Renderizar template de email
        html_content = render_to_string('emails/presupuesto_email.html', context)
        
        # Crear email
        subject = f'[Mercadito] Tu Presupuesto #{presupuesto.id} está listo'
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[presupuesto.user.email],
        )
        email.content_subtype = 'html'
        
        # Adjuntar PDF
        pdf_buffer.seek(0)
        email.attach(
            f'presupuesto_{presupuesto.id}.pdf',
            pdf_buffer.read(),
            'application/pdf'
        )
        
        # Enviar email con manejo de errores mejorado
        try:
            email.send(fail_silently=False)
            print(f"Email de presupuesto enviado correctamente a {presupuesto.user.email}")
            return True
        except Exception as email_error:
            print(f"Error específico enviando email: {email_error}")
            return False
        
    except Exception as e:
        print(f"Error general en envío de email: {e}")
        return False


def generar_pdf_presupuesto(presupuesto, request):
    """
    Genera el PDF del presupuesto y lo retorna como buffer
    """
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
        ['Cliente:', presupuesto.user.get_full_name() or presupuesto.user.username],
        ['Email:', presupuesto.user.email],
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
    return buffer


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
        
        # Generar PDF una vez
        pdf_buffer = generar_pdf_presupuesto(presupuesto, request)
        
        # Enviar email con PDF
        email_enviado = enviar_email_presupuesto(presupuesto, request)
        
        # Enviar por Telegram (copia del buffer)
        pdf_buffer_telegram = BytesIO(pdf_buffer.getvalue())
        telegram_enviado = enviar_presupuesto_telegram(request.user, presupuesto, pdf_buffer_telegram)
        
        # Mensajes de confirmación
        if email_enviado and telegram_enviado:
            messages.success(request, f'Presupuesto #{presupuesto.id} generado y enviado por email y Telegram exitosamente! 📧🤖')
        elif email_enviado:
            messages.success(request, f'Presupuesto #{presupuesto.id} generado y enviado por email exitosamente! 📧')
            if hasattr(request.user, 'profile') and request.user.profile.telegram_chat_id:
                messages.info(request, 'No se pudo enviar por Telegram. Revisa tu vinculación.')
            else:
                messages.info(request, 'Para recibir también por Telegram, vincula tu cuenta con /vincular en el bot.')
        elif telegram_enviado:
            messages.success(request, f'Presupuesto #{presupuesto.id} generado y enviado por Telegram exitosamente! 🤖')
            messages.warning(request, 'Hubo un problema enviando el email.')
        else:
            messages.success(request, f'Presupuesto #{presupuesto.id} generado exitosamente.')
            messages.warning(request, 'Hubo problemas enviando las notificaciones. Puedes descargar el PDF desde tus presupuestos.')
        
        return redirect('presupuesto:descargar_pdf', presupuesto_id=presupuesto.id)
        
    except Carrito.DoesNotExist:
        messages.error(request, 'No se encontró tu carrito.')
        return redirect('tienda:index')


@login_required
def descargar_pdf(request, presupuesto_id):
    presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id, user=request.user)
    
    # Usar la función compartida para generar PDF
    buffer = generar_pdf_presupuesto(presupuesto, request)
    
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
