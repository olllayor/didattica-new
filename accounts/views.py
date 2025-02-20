from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages  # Import the messages framework
from allauth.socialaccount.models import SocialAccount
from .forms import ProfileForm
from .models import Profile
from community.models import Post  # Import the Post model from the community app
from django.contrib.auth.decorators import login_required
import logging
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from notifications.signals import follow_created



logger = logging.getLogger(__name__)



def index(request):
    return render(request, 'index.html')

@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        if request.user.is_authenticated:
            return redirect('profile', username=request.user.username)
        return redirect('home')

    # Ensure the profile exists
    profile, created = Profile.objects.get_or_create(user=user)

    # Fetch social accounts linked to the user
    social_accounts = SocialAccount.objects.filter(user=user)

    # Fetch the user's posts
    posts = Post.objects.filter(author=user, reply_to=None).order_by('-created_at')
    reply_posts = Post.objects.filter(author=user).exclude(reply_to=None).order_by('-created_at')


    # Only allow the profile owner to edit the profile
    if request.method == 'POST':
        if request.user != user:  # Check if the current user is the profile owner
            messages.error(request, 'You do not have permission to edit this profile.')
            return redirect('profile', username=username)

        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile successfully updated!')
            return redirect('profile', username=user.username)
        else:
            if 'username' in form.errors:
                messages.error(request, 'This username is already taken. Please choose a different one.')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'user': user,
        'social_accounts': social_accounts,
        'profile': profile,
        'form': form,
        'posts': posts,
        'reply_posts': reply_posts,
    }
    return render(request, 'accounts/profile.html', context)

def search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        # Search for users and posts
        user_results = Profile.objects.filter(
            Q(user__username__icontains=query) | 
            Q(name__icontains=query)
        )
        post_results = Post.objects.filter(
            Q(content__icontains=query)
        )
        results = {
            'users': user_results,
            'posts': post_results,
        }

    return render(request, 'accounts/search.html', {'query': query, 'results': results})


@login_required
@csrf_protect
def follow_user(request, username):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user == user_to_follow:
        return JsonResponse({'error': 'You cannot follow yourself'}, status=400)

    try:
        current_user_profile = request.user.profile
        is_following = current_user_profile.is_following(user_to_follow)

        if is_following:
            # Unfollow
            current_user_profile.unfollow(user_to_follow)
            followed = False
        else:
            # Follow
            current_user_profile.follow(user_to_follow)
            followed = True
            # Trigger follow notification
            follow_created.send(sender=Profile, follower=request.user, followed_user=user_to_follow)
        # Return updated counts
        return JsonResponse({
            'followed': followed,
            'followers_count': user_to_follow.profile.get_followers_count(),
            'following_count': user_to_follow.profile.get_following_count()
        })
    except Exception as e:
        logger.error(f"Error in follow_user: {str(e)}")
        return JsonResponse({'error': 'An error occurred'}, status=500)

# accounts/views.py

@login_required
def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    followers = profile.followers.all()
    context = {
        'user': user,
        'profile': profile,
        'followers': followers,
        'is_followers_page': True,
    }
    return render(request, 'accounts/follow_list.html', context)

@login_required
def following_list(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    # Get the users that this profile is following
    following = profile.following.all()  # Changed this line to directly access following
    context = {
        'user': user,
        'profile': profile,
        'following': following,
        'is_followers_page': False,
    }
    return render(request, 'accounts/follow_list.html', context)