from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .utils import paginator


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
    context = {
        'username': username,
        'posts_count': posts_count,
    }
    context.update(paginator(request, username.posts.all()))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    username = get_object_or_404(User, posts__pk=post_id)
    posts_count = Post.objects.filter(author=username).count
    context = {
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    username = request.user.username
    if request.method == 'POST':
        form = PostForm(request.POST or None)
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
    form = PostForm(request.POST, instance=post)
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
