from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages  # Import the messages framework
from allauth.socialaccount.models import SocialAccount
from .forms import ProfileForm
from .models import Profile
import logging

logger = logging.getLogger(__name__)

def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        if request.user.is_authenticated:
            return redirect('profile', username=request.user.username)
        return redirect('home')

    # Fetch social accounts linked to the user
    social_accounts = SocialAccount.objects.filter(user=user)

    # Ensure the profile exists
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Username successfully updated!')
            return redirect('profile', username=user.username)
        else:
            if 'username' in form.errors:
                messages.error(request, 'This username is already taken. Please choose a different one.')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'user': user,
        'social_accounts': social_accounts,  # Pass social_accounts to the template
        'profile': profile,
        'form': form,
    }
    return render(request, 'accounts/profile.html', context)