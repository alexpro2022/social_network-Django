import shutil
import tempfile

from django import forms
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Comment, Group, Post, User
from .utils import get_image


USERNAME = 'author'
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
CREATE_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')
CREATE_REDIRECT_LOGIN = f'{LOGIN_URL}?next={CREATE_URL}'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='user',
            password='user_pass'
        )
        cls.author = User.objects.create_user(
            username=USERNAME,
            first_name='Ivan',
            last_name='Ivanov'
        )
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
            for field, field_type in FORMS[url].items():
                with self.subTest(url=url, field=field):
                    self.assertIsInstance(
                        self.author_client.get(url).context['form']
                        .fields[field],
                        field_type
                    )

    def test_form_pages_show_correct_context(self):
        """Шаблоны (create, edit) сформированы с правильным контекстом."""
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

    def test_authorized_create_post(self):
        """Проверка создания нового поста авторизованным пользователем."""
        posts = set(Post.objects.all())
        form_data = {
            'text': f'Тестовый пост №{len(posts) + 1}',
            'group': self.group.pk,
            'image': get_image('create.gif', 'image/gif'),
        }
        self.assertRedirects(
            self.author_client.post(CREATE_URL, data=form_data),
            PROFILE_URL
        )
        posts = set(Post.objects.all()) - posts
        self.assertEqual(len(posts), 1)
        post = posts.pop()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(
            post.image,
            f'{post._meta.get_field("image").upload_to}{form_data["image"]}'
        )
        self.assertEqual(post.author, self.author)

    def test_authorized_add_comment(self):
        """Проверка создания комментария к посту
           авторизованным пользователем."""
        form_data = {'text': 'Проверка создания комментария к посту.'}
        count = Comment.objects.count()
        self.assertRedirects(
            self.author_client.post(self.COMMENT_URL, data=form_data),
            self.POST_URL
        )
        self.assertEqual(Comment.objects.count(), count + 1)
        comment = Comment.objects.all()[0]
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.author)
        self.assertEqual(comment.post, self.post)

    def test_anonymous_create_post_or_comment(self):
        """Попытка анонима создать пост/комментарий."""
        TEXT = 'Test anonymous accsess to create post/comment'
        for url, object_, redir_url in (
            (CREATE_URL, Post, CREATE_REDIRECT_LOGIN),
            (self.COMMENT_URL, Comment, self.COMMENT_REDIRECT_LOGIN)
        ):
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.post(url, data={'text': TEXT}),
                    redir_url
                )
                self.assertFalse(
                    object_.objects.filter(text=TEXT,).exists()
                )

    def test_author_editting_post(self):
        """Проверка редактирования автором существующего поста."""
        form_data = {
            'text': f'Тестовый пост №{self.post.pk} изменен',
            'group': Group.objects.create(slug='New_group_slug').pk,
            'image': get_image('edit.gif', 'image/gif'),
        }
        self.assertRedirects(
            self.author_client.post(self.EDIT_URL, data=form_data),
            self.POST_URL
        )
        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(
            post.image,
            f'{post._meta.get_field("image").upload_to}{form_data["image"]}'
        )
        self.assertEqual(post.author, self.post.author)

    def test_anonymous_not_author_editing_post(self):
        """Попытка анонима/не-автора отредактировать пост."""
        TEXT = 'Test anonymous/not-author accsess to edit post'
        for url, client, redir_url in (
            (self.EDIT_URL, self.client, self.EDIT_REDIRECT_LOGIN),
            (self.EDIT_URL, self.another, self.POST_URL)
        ):
            with self.subTest(url=url):
                self.assertRedirects(
                    client.post(url, data={'text': TEXT}),
                    redir_url
                )
                self.assertFalse(
                    Post.objects.filter(text=TEXT,).exists()
                )
