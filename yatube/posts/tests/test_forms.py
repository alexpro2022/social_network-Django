import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import CommentForm, PostForm
from posts.models import Comment, Group, Post, User

from .utils import get_image, posts_assertEqual

USERNAME = 'author'
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
CREATE_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')
CREATE_REDIRECT_LOGIN = f'{LOGIN_URL}?next={CREATE_URL}'
IMAGE_FOLDER = Post._meta.get_field("image").upload_to
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
            image=get_image('test_image.gif', 'image.gif')
        )
        cls.COMMENT_URL = reverse('posts:add_comment', args=[cls.post.pk])
        cls.COMMENT_REDIRECT_LOGIN = f'{LOGIN_URL}?next={cls.COMMENT_URL}'
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.EDIT_REDIRECT_LOGIN = f'{LOGIN_URL}?next={cls.EDIT_URL}'
        cls.DELETE_URL = reverse('posts:post_delete', args=[cls.post.pk])
        cls.DELETE_REDIRECT_LOGIN = f'{LOGIN_URL}?next={cls.DELETE_URL}'
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another = Client()
        cls.another.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_form_fields_correct_type(self):
        """Проверка корректного типа полей формы в страницах
           создания и редактирования поста."""
        CREATE_EDIT_FORM_FIELDS = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField
        }
        FORMS = {
            CREATE_URL: CREATE_EDIT_FORM_FIELDS,
            self.EDIT_URL: CREATE_EDIT_FORM_FIELDS,
            self.POST_URL: {'text': forms.fields.CharField}
        }
        for url in FORMS:
            form = self.author_client.get(url).context['form']
            for field, field_type in FORMS[url].items():
                with self.subTest(url=url, field=field):
                    self.assertIsInstance(form.fields[field], field_type)

    def test_form_pages_show_correct_context(self):
        """Шаблоны с формами сформированы с правильным контекстом."""
        for url, form, is_edit in (
            (CREATE_URL, PostForm, False),
            (self.EDIT_URL, PostForm, True),
            (self.POST_URL, CommentForm, None)
        ):
            with self.subTest(url=url):
                context = self.author_client.get(url).context
                self.assertIsInstance(context['form'], form)
                if is_edit is not None:
                    self.assertEqual(context['is_edit'], is_edit)

# --------------Authorized/Author---------------------------
    def custom_assertEqual(self, post, author, form_data):
        self.assertEqual(post.author, author)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(post.image, f'{IMAGE_FOLDER}{form_data["image"]}')

    def test_authorized_create_post(self):
        """Проверка создания нового поста авторизованным пользователем."""
        form_data = {
            'text': 'Тестовый пост authorized_test_create',
            'group': self.group.pk,
            'image': get_image('authorized_create.gif', 'image/gif'),
        }
        posts = set(Post.objects.all())
        self.assertRedirects(
            self.author_client.post(CREATE_URL, data=form_data),
            PROFILE_URL
        )
        posts = set(Post.objects.all()) - posts
        self.assertEqual(len(posts), 1)
        post = posts.pop()
        self.custom_assertEqual(post, get_user(self.author_client), form_data)

    def test_author_edit_post(self):
        """Проверка редактирования автором существующего поста."""
        form_data = {
            'text': f'Тестовый пост №{self.post.pk} изменен',
            'group': Group.objects.create(slug='New_group_slug').pk,
            'image': get_image('author_edit.gif', 'image/gif'),
        }
        self.assertRedirects(
            self.author_client.post(self.EDIT_URL, data=form_data),
            self.POST_URL
        )
        post = Post.objects.get(pk=self.post.pk)
        self.custom_assertEqual(post, self.post.author, form_data)

    def test_author_delete_post(self):
        """Проверка удаления поста автором."""
        self.assertIn(self.post, Post.objects.all())
        self.assertRedirects(
            self.author_client.post(self.DELETE_URL),
            PROFILE_URL
        )
        self.assertNotIn(self.post, Post.objects.all())

# -----------Anonymous/Not_author------------------------
    def test_anonymous_create_post(self):
        """Попытка анонима создать пост."""
        form_data = {
            'text': 'Тестовый пост anonymous_test_create',
            'group': self.group.pk,
            'image': get_image('anonymous_create.gif', 'image/gif'),
        }
        posts = set(Post.objects.all())
        self.assertRedirects(
            self.client.post(CREATE_URL, data=form_data),
            CREATE_REDIRECT_LOGIN
        )
        self.assertEqual(set(Post.objects.all()), posts)

    def test_anonymous_or_not_author_cannot_edit_or_delete_post(self):
        """Попытка анонима или не-автора отредактировать или удалить пост."""
        group = Group.objects.create(slug='New_group_slug')
        anonymous = {
            'text': 'Test anonymous to edit post',
            'group': group.pk,
            'image': get_image('anonymous_edit.gif', 'image/gif'),
        }
        another = {
            'text': 'Test another to edit post',
            'group': group.pk,
            'image': get_image('another_edit.gif', 'image/gif'),
        }
        for client, url, redir_url, form_data in (
            (self.client, self.EDIT_URL, self.EDIT_REDIRECT_LOGIN, anonymous),
            (self.client, self.DELETE_URL, self.DELETE_REDIRECT_LOGIN, None),
            (self.another, self.EDIT_URL, self.POST_URL, another),
            (self.another, self.DELETE_URL, self.POST_URL, None),
        ):
            with self.subTest(client=get_user(client), url=url):
                self.assertRedirects(
                    client.post(url, data=form_data),
                    redir_url
                )
                posts_assertEqual(
                    self,
                    self.post,
                    Post.objects.get(pk=self.post.pk)
                )

# -------------Comments------------------------
    def test_authorized_add_comment(self):
        """Проверка создания комментария к посту
           авторизованным пользователем."""
        form_data = {'text': 'Проверка создания комментария к посту.'}
        comments = set(Comment.objects.all())
        self.assertRedirects(
            self.another.post(self.COMMENT_URL, data=form_data),
            self.POST_URL
        )
        comments = set(Comment.objects.all()) - comments
        self.assertEqual(len(comments), 1)
        comment = comments.pop()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, get_user(self.another))
        self.assertEqual(comment.post, self.post)

    def test_anonymous_add_comment(self):
        """Попытка анонима создать комментарий."""
        form_data = {'text': 'Test anonymous to create comment'}
        comments = set(Comment.objects.all())
        self.assertRedirects(
            self.client.post(self.COMMENT_URL, data=form_data),
            self.COMMENT_REDIRECT_LOGIN
        )
        self.assertEqual(set(Comment.objects.all()), comments)
