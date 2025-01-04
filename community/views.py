from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment, PostImage
from .forms import PostForm, CommentForm
from django.contrib import messages

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
    comment_form = CommentForm()
    return render(
        request, "community/feed.html", {"posts": posts, "comment_form": comment_form}
    )


def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect("feed")
