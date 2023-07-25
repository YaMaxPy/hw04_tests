from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginator

WAIT_TIME_SEC: int = 20


@cache_page(WAIT_TIME_SEC, key_prefix='index_page')
def index(request):
    post_list = paginator(request, Post.objects.all())
    return render(request, 'posts/index.html', post_list)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
        'posts': posts,
    }
    context.update(paginator(request, posts))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    username = get_object_or_404(User, username=username)
    posts_count = username.posts.all().count
    if request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=username
    ).exists():
        following = True
    else:
        following = False
    context = {
        'username': username,
        'posts_count': posts_count,
        'following': following,
    }
    context.update(paginator(request, username.posts.all()))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    context = {
        'post': post,
        'comments': post.comments.all(),
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    username = request.user.username
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None
        )
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            form.save()
            return redirect('posts:profile', username)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'GET':
        if request.user != post.author:
            return redirect('posts:post_detail', post_id)
        form = PostForm(instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)

    return render(request, 'posts/create_post.html', {'form': form,
                                                      'post': post,
                                                      'is_edit': True})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = paginator(request, Post.objects.filter(
        author__following__user=request.user)
    )
    return render(request, 'posts/follow.html', post_list)


@login_required
def profile_follow(request, username):
    user = request.user
    username = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=user, author=username)
    if user != username and not following.exists():
        Follow.objects.create(user=user, author=username)
    context = {
        'username': username,
        'following': following,
    }
    context.update(paginator(request, username.posts.all()))
    return render(request, 'posts/profile.html', context)


@login_required
def profile_unfollow(request, username):
    user = request.user
    username = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=user, author=username)
    if following.exists():
        following.delete()
    context = {
        'username': username,
        'following': following,
    }
    context.update(paginator(request, username.posts.all()))
    return render(request, 'posts/profile.html', context)
