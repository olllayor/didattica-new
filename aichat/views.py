from django.shortcuts import render
from django.http import JsonResponse

def chat_view(request):
    # Check if request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'ai/chat-modal.html')
    return render(request, 'ai/chat_noid.html')

def check_device(request):
    # Simple mobile detection
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad'])
    return JsonResponse({'is_mobile': is_mobile})
