import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .utils import get_image, posts_assertEqual
from posts.models import Comment, Follow, Group, Post, User
from yatube.settings import POSTS_PER_PAGE


SLUG = 'Test-slug'
NEW_TEST_SLUG = 'New_test_slug'
USERNAME = 'author'
INDEX_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
NEW_GROUP_URL = reverse('posts:group_list', args=[NEW_TEST_SLUG])
FOLLOW_INDEX_URL = reverse('posts:follow_index')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username=USERNAME)
        cls.follower_author = User.objects.create_user(username='follower')
        Group.objects.create(slug=NEW_TEST_SLUG)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
            image=get_image('test_image.gif', 'image.gif')
        )
        cls.comment = Comment.objects.create(
            text='Текст комментария',
            author=cls.author,
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            user=cls.follower_author,
            author=cls.author
        )
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.user_client = Client()
        cls.author_client = Client()
        cls.follower_author_client = Client()
        cls.user_client.force_login(cls.user)
        cls.author_client.force_login(cls.author)
        cls.follower_author_client.force_login(cls.follower_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_paginator(self):
        """Проверяем корректную работу паджинатора."""
        POSTS_ON_PAGE_2 = 3
        PAGE_2 = '?page=2'
        Post.objects.bulk_create(
            Post(author=self.author, group=self.group)
            for _ in range(POSTS_PER_PAGE + POSTS_ON_PAGE_2 - 1)
        )
        for url, expected_value in (
            (INDEX_URL, POSTS_PER_PAGE),
            (INDEX_URL + PAGE_2, POSTS_ON_PAGE_2),
            (GROUP_URL, POSTS_PER_PAGE),
            (GROUP_URL + PAGE_2, POSTS_ON_PAGE_2),
            (PROFILE_URL, POSTS_PER_PAGE),
            (PROFILE_URL + PAGE_2, POSTS_ON_PAGE_2),
            (FOLLOW_INDEX_URL, POSTS_PER_PAGE),
            (FOLLOW_INDEX_URL + PAGE_2, POSTS_ON_PAGE_2)
        ):
            with self.subTest(url=url):
                self.assertEqual(
                    len(self.follower_author_client.get(url)
                        .context['page_obj']),
                    expected_value
                )

    def test_cache(self):
        """Проверяем, что после удаления записи контент главной страницы не меняется.
           После очистки кеша, контент главной страницы изменился."""
        init_content = self.client.get(INDEX_URL).content
        Post.objects.all().delete()
        self.assertEqual(init_content, self.client.get(INDEX_URL).content)
        cache.clear()
        self.assertNotEqual(init_content, self.client.get(INDEX_URL).content)

    def test_intact_post_in_list_pages_context(self):
        """Проверка словаря контекста предаваемого в шаблоны.
           Пост попал на ленты и на "детали" без искажений."""
        for url, object_ in (
            (INDEX_URL, 'page_obj'),
            (GROUP_URL, 'page_obj'),
            (PROFILE_URL, 'page_obj'),
            (FOLLOW_INDEX_URL, 'page_obj'),
            (self.POST_URL, 'post'),
        ):
            with self.subTest(url=url):
                temp = self.follower_author_client.get(url).context[object_]
                if object_ == 'page_obj':
                    self.assertEqual(len(temp), 1)
                    temp = temp[0]
                post = temp
                posts_assertEqual(self, post, self.post)

    def test_intact_author_in_profile_context(self):
        """Автор в контексте Профиля без искажений."""
        self.assertEqual(
            self.author,
            self.client.get(PROFILE_URL).context['author']
        )

    def test_intact_group_in_group_list_context(self):
        """Группа в контексте Групп-ленты без искажений."""
        group = self.client.get(GROUP_URL).context['group']
        self.assertEqual(group, self.group)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)

    def test_post_not_in_incorrect_list(self):
        """Проверяем, что пост не попал на чужую:
            1. групп-ленту.
            2. ленту подписок."""
        new_post = Post.objects.create(author=self.user)
        for post, client, url in (
            (self.post, self.client, NEW_GROUP_URL),
            (new_post, self.follower_author_client, FOLLOW_INDEX_URL)
        ):
            with self.subTest(url=url):
                self.assertNotIn(post, client.get(url).context['page_obj'])

    def test_no_author_self_follow(self):
        """Автор не может подписываться на самого себя."""
        self.author_client.get(PROFILE_FOLLOW_URL)
        self.assertFalse(
            Follow.objects.filter(
                user=self.author,
                author=self.author
            ).exists()
        )

    def test_authenticated_user_follow_author(self):
        """Авторизованный пользователь (не автор) может подписываться
           на других пользователей."""
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )
        self.user_client.get(PROFILE_FOLLOW_URL)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )

    def test_authenticated_user_unfollow_author(self):
        """Авторизованный пользователь (не автор) может удалять других
           пользователей из подписок."""
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower_author,
                author=self.author
            ).exists()
        )
        self.follower_author_client.get(PROFILE_UNFOLLOW_URL)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )
