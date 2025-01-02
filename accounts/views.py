from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount

@login_required
def profile(request):
    user = request.user
    social_accounts = SocialAccount.objects.filter(user=user)
    context = {
        'user': user,
        'social_accounts': social_accounts,
    }
    return render(request, 'accounts/profile.html', context)