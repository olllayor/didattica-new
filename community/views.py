from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from .models import Post, Comment, PostImage
from .forms import PostForm, CommentForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Reaction
from django.utils import timezone


@login_required
def create_post(request):
    if request.method == "POST":
        # Check if user can post
        if not request.user.profile.can_post():
            remaining_time = (
                100
                - (timezone.now() - request.user.profile.last_post_time).total_seconds()
            )
            messages.error(
                request,
                f"Please wait {int(remaining_time)} seconds before creating another post.",
            )
            return redirect("feed")

        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # Handle reposts
            shared_post_id = form.cleaned_data.get("shared_post")
            if shared_post_id:
                shared_post = get_object_or_404(Post, id=shared_post_id)
                post.shared_post = shared_post

            # Handle replies
            reply_to_id = form.cleaned_data.get("reply_to")
            if reply_to_id:
                reply_to = get_object_or_404(Post, id=reply_to_id)
                post.reply_to = reply_to

            post.save()

            # Handle multiple image uploads
            images = request.FILES.getlist("images")  # Get list of uploaded images
            for image in images:
                PostImage.objects.create(post=post, image=image)

            # Update last post time
            request.user.profile.last_post_time = timezone.now()
            request.user.profile.save()

            if post.status == "published":
                messages.success(request, "Post published successfully!")
                return redirect("feed")
            else:
                messages.success(request, "Post saved as draft.")
                return redirect("profile", username=request.user.username)
        else:
            # Print form errors for debugging
            print(form.errors)
            messages.error(
                request, "Failed to create post. Please check the form."
            )  # Error message
    else:
        form = PostForm()
    return render(request, "community/create_post.html", {"form": form})


# community/views.py
def feed(request):
    posts = Post.objects.filter(reply_to=None).order_by("-created_at")
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get("page", 1)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({"posts": [], "has_next": False})

    # Track viewed posts in the session
    if "viewed_posts" not in request.session:
        request.session["viewed_posts"] = []

    posts_data = []
    for post in page_obj:
        if post.id not in request.session["viewed_posts"]:
            post.views += 1
            post.save()
            request.session["viewed_posts"].append(post.id)
            request.session.modified = True  # Save the session

        # Include reactions in the response
        reactions = [
            {"reaction": reaction.reaction} for reaction in post.reactions.all()
        ]

        posts_data.append(
            {
                "id": post.id,
                "author": post.author.username,
                "content": post.content,
                "image": post.image.url if post.image else None,
                "likes_count": post.get_likes_count(),
                "comments_count": post.get_comments_count(),
                "views": post.views,
                "created_at": post.created_at.strftime("%b %d, %Y %I:%M %p"),
                "profile_image": (
                    post.author.profile.profile_image.url
                    if post.author.profile.profile_image
                    else None
                ),
                "is_liked": request.user in post.likes.all(),
                "reactions": reactions,  # Include reactions
            }
        )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"posts": posts_data, "has_next": page_obj.has_next()})

    comment_form = CommentForm()
    return render(
        request,
        "community/feed.html",
        {"posts": page_obj, "comment_form": comment_form},
    )


@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    # Toggle like
    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({"liked": liked, "likes_count": post.likes.count()})


@login_required
def check_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_liked = request.user in post.likes.all()
    return JsonResponse({"is_liked": is_liked})


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return JsonResponse(
            {
                "success": True,
                "comment": {
                    "content": comment.content,
                    "author": comment.author.username,
                    "created_at": comment.created_at.strftime("%b %d, %Y %I:%M %p"),
                },
            }
        )
    else:
        return JsonResponse({"success": False, "errors": form.errors})


def share_post(request, post_id):
    original_post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            shared_post = form.save(commit=False)
            shared_post.author = request.user
            shared_post.shared_post = original_post
            shared_post.save()
            messages.success(request, "Post shared successfully!")
            return redirect("feed")
    else:
        form = PostForm()
    return render(
        request,
        "community/share_post.html",
        {"form": form, "original_post": original_post},
    )


@require_POST
def react_to_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    reaction = request.POST.get("reaction")

    # Validate reaction
    if reaction not in dict(Reaction.REACTION_CHOICES).keys():
        return JsonResponse({"success": False, "error": "Invalid reaction"}, status=400)

    # Update or create the reaction
    reaction_obj, created = Reaction.objects.update_or_create(
        post=post, user=request.user, defaults={"reaction": reaction}
    )

    # Get all reactions for the post
    reactions = post.reactions.all()
    reaction_counts = {}
    for r in reactions:
        if r.reaction in reaction_counts:
            reaction_counts[r.reaction] += 1
        else:
            reaction_counts[r.reaction] = 1

    # Prepare the response
    reaction_list = [{"reaction": k, "count": v} for k, v in reaction_counts.items()]

    return JsonResponse(
        {
            "success": True,
            "reactions": reaction_list,
        }
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    replies = Post.objects.filter(reply_to=post).order_by("-created_at")

    # Track view
    if "viewed_posts" not in request.session:
        request.session["viewed_posts"] = []

    if post.id not in request.session["viewed_posts"]:
        post.views += 1
        post.save()
        request.session["viewed_posts"].append(post.id)
        request.session.modified = True

    return render(
        request, "community/post_detail.html", {"post": post, "replies": replies}
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return JsonResponse({
        'content': post.content,
        'image': post.image.url if post.image else None,
    })
