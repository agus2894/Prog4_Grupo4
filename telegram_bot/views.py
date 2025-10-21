from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def vincular_telegram(request):
    """Página para vincular cuenta con Telegram"""
    
    if request.method == 'POST':
        chat_id = request.POST.get('chat_id', '').strip()
        
        if chat_id:
            # Guardar chat_id en el perfil
            request.user.profile.telegram_chat_id = chat_id
            request.user.profile.save()
            
            messages.success(request, '¡Telegram vinculado exitosamente! 🤖 Ahora recibirás notificaciones.')
            return redirect('telegram_bot:vincular')
        else:
            messages.error(request, 'Por favor ingresa un Chat ID válido.')
    
    context = {
        'user_telegram_id': request.user.profile.telegram_chat_id if hasattr(request.user, 'profile') else None,
    }
    
    return render(request, 'telegram_bot/vincular.html', context)
