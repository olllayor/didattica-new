from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from .forms import ProfileForm
from .models import Profile

def profile(request, username):
    user = get_object_or_404(User, username=username)
    social_accounts = SocialAccount.objects.filter(user=user)
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=user.username)  # Redirect to the updated profile URL
    else:
        form = ProfileForm(instance=profile)

    context = {
        'user': user,
        'social_accounts': social_accounts,
        'profile': profile,
        'form': form,
    }
    return render(request, 'accounts/profile.html', context)