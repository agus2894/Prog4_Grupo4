from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import ChatMessage

@login_required
def chat_view(request):
    return render(request, "simple_chat/chat.html")

@login_required
def messages_api(request):
    after = request.GET.get("after_id")
    qs = ChatMessage.objects.all().order_by('created_at')
    if after:
        qs = qs.filter(id__gt=int(after))
    msgs = [
        {
            "id": m.id,
            "user": m.user.username if m.user else "Anónimo",
            "text": m.text,
            "created_at": m.created_at.isoformat(),
        }
        for m in qs
    ]
    return JsonResponse({"messages": msgs})

@require_POST
@login_required
def post_message_api(request):
    user = request.user
    text = request.POST.get("text", "").strip()
    if not text:
        return JsonResponse({"error": "Mensaje vacío"}, status=400)
    if len(text) > 500:
        return JsonResponse({"error": "Mensaje muy largo"}, status=400)
    
    m = ChatMessage.objects.create(user=user, text=text)
    return JsonResponse({
        "id": m.id, 
        "created_at": m.created_at.isoformat(),
        "success": True
    })
