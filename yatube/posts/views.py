from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
# from django.views.decorators.cache import cache_page
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from yatube.settings import POSTS_PER_PAGE


def paginator(request, posts, per_page):
    return Paginator(posts, per_page).get_page(request.GET.get('page'))


# @cache_page(20, key_prefix='index_page')
def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': paginator(request, Post.objects.all(), POSTS_PER_PAGE)
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': paginator(request, group.posts.all(), POSTS_PER_PAGE)
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=User.objects.get(username=username)
    ).exists():
        following = True
    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': paginator(request, author.posts.all(), POSTS_PER_PAGE),
        'following': following
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': Comment.objects.filter(post=post)
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form, 'is_edit': False
        })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form, 'is_edit': True
        })
    form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    return render(request, 'posts/follow.html', {
        'page_obj': paginator(request, posts, POSTS_PER_PAGE)
    })


@login_required
def profile_follow(request, username):
    following_author = User.objects.get(username=username)
    if following_author != request.user and not Follow.objects.filter(
        user=request.user,
        author=following_author
    ).exists():
        Follow.objects.create(
            user=request.user,
            author=following_author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    following_author = User.objects.get(username=username)
    follow = Follow.objects.filter(
        user=request.user,
        author=following_author
    )
    if follow.exists():
        follow.delete()
    return redirect('posts:profile', username=username)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/delete_post.html'
    success_url = reverse_lazy('posts:index')
