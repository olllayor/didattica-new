from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ai.models import AIModel, UserAPIToken

@login_required
def chat_view(request):
    ai_models = AIModel.objects.filter(is_active=True)
    user_token = UserAPIToken.objects.filter(user=request.user).first()
    
    # Get post context from request
    post_id = request.GET.get('post_id')
    post_content = request.GET.get('content', '')
    post_image = request.GET.get('image', '')
    
    context = {
        'ai_models': ai_models,
        'has_token': bool(user_token),
        'post_content': post_content,
        'post_image': post_image,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'ai/chat-modal.html', context)
    return render(request, 'ai/chat_noid.html', context)

@login_required
def save_api_token(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        if token:
            UserAPIToken.objects.update_or_create(
                user=request.user,
                defaults={'openrouter_token': token}
            )
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def check_device(request):
    # Simple mobile detection
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad'])
    return JsonResponse({'is_mobile': is_mobile})
