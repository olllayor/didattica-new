from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from .models import Post, Comment, PostImage
from .forms import PostForm, CommentForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            # Handle multiple image uploads
            images = request.FILES.getlist('images')  # Get list of uploaded images
            for image in images:
                PostImage.objects.create(post=post, image=image)

            messages.success(request, "Post created successfully!")  # Success message
            return redirect("feed")
        else:
            messages.error(request, "Failed to create post. Please check the form.")  # Error message
    else:
        form = PostForm()
    return render(request, "community/create_post.html", {"form": form})


def feed(request):
    posts = Post.objects.all().order_by("-created_at")
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get("page", 1)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        # If the page is out of range, return an empty list
        return JsonResponse({"posts": [], "has_next": False})

    # Track viewed posts in the session
    if "viewed_posts" not in request.session:
        request.session["viewed_posts"] = []

    for post in page_obj:
        if post.id not in request.session["viewed_posts"]:
            post.views += 1
            post.save()
            request.session["viewed_posts"].append(post.id)
            request.session.modified = True  # Save the session

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # Return JSON for AJAX requests
        posts_data = [
            {
                "id": post.id,
                "author": post.author.username,
                "content": post.content,
                "image": post.image.url if post.image else None,
                "likes_count": post.get_likes_count(),
                "comments_count": post.get_comments_count(),
                "views": post.views,
                "created_at": post.created_at.strftime("%b %d, %Y %I:%M %p"),
            }
            for post in page_obj
        ]
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
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return JsonResponse({
            "success": True,
            "comment": {
                "content": comment.content,
                "author": comment.author.username,
                "created_at": comment.created_at.strftime("%b %d, %Y %I:%M %p"),
            },
        })
    else:
        return JsonResponse({"success": False, "errors": form.errors})