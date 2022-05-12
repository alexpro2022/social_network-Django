from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User
from .utils import get_image
from yatube.settings import POSTS_PER_PAGE


SLUG = 'Test-slug'
USERNAME = 'author'
INDEX_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
FOLLOW_URL = reverse('posts:follow_index')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username=USERNAME,
            first_name='Ivan',
            last_name='Ivanov'
        )
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
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.user = User.objects.create_user(username='nonameuser')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.follow = Follow.objects.create(user=cls.author, author=cls.user)

    def setUp(self):
        self.client.force_login(self.author)

    def test_paginator(self):
        """Проверяем корректную работу паджинатора."""
        POSTS_ON_PAGE_2 = 3
        PAGE_2 = '?page=2'
        Post.objects.bulk_create(
            Post(author=self.author, group=self.group)
            for _ in range(POSTS_PER_PAGE + POSTS_ON_PAGE_2 - 1)
        )
        Follow.objects.create(user=self.user, author=self.author)
        for url, expected_value in (
            (INDEX_URL, POSTS_PER_PAGE),
            (INDEX_URL + PAGE_2, POSTS_ON_PAGE_2),
            (GROUP_URL, POSTS_PER_PAGE),
            (GROUP_URL + PAGE_2, POSTS_ON_PAGE_2),
            (PROFILE_URL, POSTS_PER_PAGE),
            (PROFILE_URL + PAGE_2, POSTS_ON_PAGE_2),
            (FOLLOW_URL, POSTS_PER_PAGE),
            (FOLLOW_URL + PAGE_2, POSTS_ON_PAGE_2)
        ):
            with self.subTest(url=url):
                self.assertEqual(
                    len(self.auth_user.get(url).context['page_obj']),
                    expected_value
                )

    def test_intact_post_in_list_pages_context(self):
        """Проверка словаря контекста предаваемого в шаблоны.
           Пост попал на ленты и на "детали" без искажений."""
        Follow.objects.create(user=self.user, author=self.author)
        for url, object_ in (
            (INDEX_URL, 'page_obj'),
            (GROUP_URL, 'page_obj'),
            (PROFILE_URL, 'page_obj'),
            (FOLLOW_URL, 'page_obj'),
            (self.POST_URL, 'post'),
        ):
            with self.subTest(url=url):
                temp_result = self.auth_user.get(url).context[object_]
                if object_ == 'page_obj':
                    self.assertEqual(len(temp_result), 1)
                    temp_result = temp_result[0]
                post = temp_result
                self.assertEqual(post, self.post)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.image, self.post.image)

    def test_intact_author_in_profile_context(self):
        """Автор в контексте Профиля без искажений."""
        context = self.client.get(PROFILE_URL).context
        author = context['author']
        self.assertEqual(author, self.author)
        self.assertEqual(author.username, self.author.username)
        self.assertEqual(author.first_name, self.author.first_name)
        self.assertEqual(author.last_name, self.author.last_name)
        self.assertIsInstance(context['following'], bool)

    def test_intact_comment_in_post_detail_context(self):
        """Комментарий в контексте страницы деталей поста.
           Комментарий попал без искажений."""
        comments = self.client.get(self.POST_URL).context['comments']
        self.assertEqual(len(comments), 1)
        comment = comments[0]
        self.assertEqual(self.comment, comment)
        self.assertEqual(self.comment.text, comment.text)
        self.assertEqual(self.comment.author, comment.author)
        self.assertEqual(self.comment.post, comment.post)

    def test_intact_group_in_group_list_context(self):
        """Группа в контексте Групп-ленты без искажений."""
        group = self.client.get(GROUP_URL).context['group']
        self.assertEqual(group, self.group)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)

    def test_post_not_in_incorrect_group_list(self):
        """Проверяем, что пост не попал на чужую Групп-ленту. Создаем новую группу
           и проверяем непопадание поста из фикстуры на ленту новой группы."""
        Group.objects.create(
            title='Новая Тестовая группа',
            slug='New_test_slug'
        )
        self.assertNotIn(
            self.post,
            self.client.get(reverse(
                'posts:group_list', args=['New_test_slug'])
            ).context['page_obj']
        )

    def test_profile_follow_unfollow(self):
        """Авторизованный пользователь (не автор) может подписываться
           на других пользователей и удалять их из подписок."""
        self.assertEqual(Follow.objects.count(), 1)
        # проверяем, что автор не работает:
        self.client.get(PROFILE_FOLLOW_URL)
        self.assertEqual(Follow.objects.count(), 1)
        self.client.get(PROFILE_UNFOLLOW_URL)
        self.assertEqual(Follow.objects.count(), 1)
        # проверяем, что не автор работает:
        follows = set(Follow.objects.all())
        self.auth_user.get(PROFILE_FOLLOW_URL)
        self.assertEqual(Follow.objects.count(), 2)
        follows = set(Follow.objects.all()) - follows
        follow = follows.pop()
        self.assertEqual(follow.user, self.user)
        self.assertEqual(follow.author, self.author)
        self.auth_user.get(PROFILE_UNFOLLOW_URL)
        self.assertEqual(Follow.objects.count(), 1)
        self.assertNotIn(follow, Follow.objects.all())

    def test_follow_index(self):
        """Новая запись пользователя появляется в ленте тех, кто на него подписан
           и не появляется в ленте тех, кто не подписан."""
        follower_author = User.objects.create_user(username='follower_author')
        follower_author_client = Client()
        follower_author_client.force_login(follower_author)
        Follow.objects.create(user=follower_author, author=self.author)
        new_post = Post.objects.create(
            text='New post for follow_index test',
            author=self.user,
        )
        self.assertNotIn(
            new_post,
            follower_author_client.get(FOLLOW_URL).context['page_obj']
        )
        self.assertIn(
            new_post,
            self.client.get(FOLLOW_URL).context['page_obj']
        )
