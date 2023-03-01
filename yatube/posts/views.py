from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, GroupFollow, Post, User

from yatube.settings import POSTS_PER_PAGE


def paginator(request, objects, per_page):
    return Paginator(objects, per_page).get_page(request.GET.get('page'))


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': paginator(request, Post.objects.all(), POSTS_PER_PAGE)
    })


def authors(request):
    return render(request, 'posts/authors.html', {
        'page_obj': paginator(request, User.objects.all(), 3)
    })


def authors_follow(request):
    authors = User.objects.filter(following__user=request.user)
    return render(request, 'posts/authors_follow.html', {
        'page_obj': paginator(request, authors, 3)
    })


def groups(request):
    return render(request, 'posts/groups.html', {
        'page_obj': paginator(request, Group.objects.all(), 3)
    })


def groups_follow(request):
    groups = Group.objects.filter(group_following__user=request.user)
    return render(request, 'posts/groups_follow.html', {
        'page_obj': paginator(request, groups, 3)
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': paginator(request, group.posts.all(), POSTS_PER_PAGE),
        'following': (
            request.user.is_authenticated
            and GroupFollow.objects.filter(
                user=request.user,
                group=group).exists()
        )
    })


def group_description(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(
        request,
        'posts/includes/views/group_description.html',
        {'group': group,
         'following': (
             request.user.is_authenticated
             and GroupFollow.objects.filter(
                 user=request.user,
                 group=group).exists()
         )}
    )


def profile_generic(request, author, page_obj, template_name):
    return render(request, template_name, {
        'author': author,
        'page_obj': page_obj,
        'following': (
            request.user.is_authenticated
            and request.user != author
            and Follow.objects.filter(
                user=request.user,
                author=author).exists()
        )
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    return profile_generic(
        request,
        author,
        paginator(request, author.posts.all(), POSTS_PER_PAGE),
        'posts/profile.html'
    )


def profile_comments(request, username):
    author = get_object_or_404(User, username=username)
    return profile_generic(
        request,
        author,
        paginator(request, author.comments.all(), POSTS_PER_PAGE),
        'posts/profile_content/profile_comments.html'
    )


def profile_following(request, username):
    """Вывод списка пользователей, подписанных на автора."""
    author = get_object_or_404(User, username=username)
    return profile_generic(
        request,
        author,
        paginator(
            request,
            User.objects.filter(follower__author=author),
            POSTS_PER_PAGE),
        'posts/profile_content/profile_following.html'
    )


def profile_follower(request, username):
    """Вывод списка авторов, на которых подписан пользователь."""
    follower = get_object_or_404(User, username=username)
    return profile_generic(
        request,
        follower,
        paginator(
            request,
            User.objects.filter(following__user=follower),
            POSTS_PER_PAGE),
        'posts/profile_content/profile_follower.html'
    )


def profile_group_follower(request, username):
    """Вывод списка групп, на которые подписан пользователь."""
    follower = get_object_or_404(User, username=username)
    groups = Group.objects.filter(group_following__user=follower)
    return profile_generic(
        request,
        follower,
        paginator(request, groups, 3),
        'posts/profile_content/profile_group_follower.html'
    )


def post_detail(request, post_id):
    return render(request, 'posts/post_detail.html', {
        'post': get_object_or_404(Post, id=post_id),
        'form': CommentForm()
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
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    if request.method == 'POST':
        author = post.author
        post.delete()
        return redirect('posts:profile', username=author)
    return render(request, 'posts/delete_post.html', {
        'post': post
    })


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
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author)
    return redirect('posts:profile', username=username)


@login_required
def group_follow(request, slug):
    GroupFollow.objects.get_or_create(
        user=request.user,
        group=get_object_or_404(Group, slug=slug))
    return redirect('posts:group_list', slug=slug)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        request.user.follower,
        author__username=username
    ).delete()
    return redirect('posts:profile', username=username)


@login_required
def group_unfollow(request, slug):
    get_object_or_404(
        request.user.group_follower,
        group__slug=slug
    ).delete()
    return redirect('posts:group_list', slug=slug)
