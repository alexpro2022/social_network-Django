from django.contrib.auth import get_user
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post, User

SLUG = 'Test-slug'
USERNAME = 'author'
INDEX_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
FOLLOW_URL = reverse('posts:follow_index')
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])
FOLLOW_REDIRECT_LOGIN = f'{LOGIN_URL}?next={PROFILE_FOLLOW_URL}'
UNFOLLOW_REDIRECT_LOGIN = f'{LOGIN_URL}?next={PROFILE_UNFOLLOW_URL}'
CREATE_REDIRECT_LOGIN = f'{LOGIN_URL}?next={CREATE_URL}'
PAGE_NOT_EXIST_URL = '/unexisting_page/'
OK, FOUND, NOT_FOUND = 200, 302, 404


class PostURLsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
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
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.EDIT_REDIRECT_LOGIN = f'{LOGIN_URL}?next={cls.EDIT_URL}'
        cls.another = Client()
        cls.author_client = Client()
        cls.another.force_login(cls.user)
        cls.author_client.force_login(cls.author)

    def test_url_status_code(self):
        """Проверяет доступность страницы по указанному адресу."""
        for url, client, status_code in (
            (INDEX_URL, self.client, OK),
            (GROUP_URL, self.client, OK),
            (self.POST_URL, self.client, OK),
            (PROFILE_URL, self.client, OK),
            (FOLLOW_URL, self.client, FOUND),
            (FOLLOW_URL, self.another, OK),
            (PROFILE_FOLLOW_URL, self.client, FOUND),
            (PROFILE_FOLLOW_URL, self.another, FOUND),
            (PROFILE_FOLLOW_URL, self.author_client, FOUND),
            (PROFILE_UNFOLLOW_URL, self.client, FOUND),
            (PROFILE_UNFOLLOW_URL, self.another, FOUND),
            (PROFILE_UNFOLLOW_URL, self.author_client, NOT_FOUND),
            (CREATE_URL, self.client, FOUND),
            (CREATE_URL, self.another, OK),
            (self.EDIT_URL, self.client, FOUND),
            (self.EDIT_URL, self.another, FOUND),
            (self.EDIT_URL, self.author_client, OK),
            (PAGE_NOT_EXIST_URL, self.author_client, NOT_FOUND),
        ):
            with self.subTest(url=url, client=client):
                self.assertEqual(
                    client.get(url).status_code,
                    status_code
                )

    def test_properly_redirect_user_with_no_access_rights_(self):
        """Перенаправляем пользователя на соответствующую страницу."""
        for url, client, finish in (
            (CREATE_URL, self.client, CREATE_REDIRECT_LOGIN),
            (self.EDIT_URL, self.client, self.EDIT_REDIRECT_LOGIN),
            (self.EDIT_URL, self.another, self.POST_URL),
            (PROFILE_FOLLOW_URL, self.client, FOLLOW_REDIRECT_LOGIN),
            (PROFILE_FOLLOW_URL, self.another, PROFILE_URL),
            (PROFILE_FOLLOW_URL, self.author_client, PROFILE_URL),
            (PROFILE_UNFOLLOW_URL, self.client, UNFOLLOW_REDIRECT_LOGIN),
            (PROFILE_UNFOLLOW_URL, self.another, PROFILE_URL)
        ):
            with self.subTest(
                url=url,
                username=get_user(client).username,
                finish=finish
            ):
                self.assertRedirects(client.get(url), finish)

    def test_url_uses_correct_template(self):
        """Проверка шаблона для указанного адреса."""
        for url, template in {
            INDEX_URL: 'posts/index.html',
            GROUP_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.POST_URL: 'posts/post_detail.html',
            CREATE_URL: 'posts/create_post.html',
            self.EDIT_URL: 'posts/create_post.html',
            FOLLOW_URL: 'posts/follow.html',
        }.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.author_client.get(url),
                    template
                )
