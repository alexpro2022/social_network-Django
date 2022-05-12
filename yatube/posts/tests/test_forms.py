import shutil
import tempfile

from django import forms

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Comment, Group, Post, User
from .utils import get_image


USERNAME = 'author'
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
CREATE_URL = reverse('posts:post_create')
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.pk])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client.force_login(self.author)

    def test_form_pages_show_correct_context(self):
        """Шаблоны (create, edit) сформированы с правильным контекстом."""
        for url, is_edit in {CREATE_URL: False, self.EDIT_URL: True}.items():
            with self.subTest(url=url):
                context = self.client.get(url).context
                self.assertIsInstance(context['form'], PostForm)
                self.assertEqual(context['is_edit'], is_edit)

    def test_form_fields_correct_type(self):
        """Проверка корректного типа полей формы."""
        FORM_FIELDS = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField
        }
        for url in (CREATE_URL, self.EDIT_URL):
            for field, field_type in FORM_FIELDS.items():
                with self.subTest(url=url, field=field):
                    self.assertIsInstance(
                        self.client.get(url).context['form'].fields[field],
                        field_type
                    )

    def test_create_post(self):
        """Проверка создания нового поста."""
        posts = set(Post.objects.all())
        form_data = {
            'text': f'Тестовый пост №{len(posts) + 1}',
            'group': self.group.pk,
            'image': get_image('create.gif', 'image/gif'),
        }
        self.assertRedirects(
            self.client.post(CREATE_URL, data=form_data),
            PROFILE_URL
        )
        posts = set(Post.objects.all()) - posts
        self.assertEqual(len(posts), 1)
        post = posts.pop()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(post.image, f'posts/{form_data["image"]}')
        self.assertEqual(post.author, self.author)

    def test_update_post(self):
        """Проверка редактирования существующего поста."""
        form_data = {
            'text': f'Тестовый пост №{self.post.pk} изменен',
            'group': Group.objects.create(slug='New_group_slug').pk,
            'image': get_image('edit.gif', 'image/gif'),
        }
        self.assertRedirects(
            self.client.post(self.EDIT_URL, data=form_data),
            self.POST_URL
        )
        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(post.image, f'posts/{form_data["image"]}')
        self.assertEqual(post.author, self.post.author)

    def test_post_detail_page_form_in_context(self):
        form = self.client.get(self.POST_URL).context['form']
        self.assertIsInstance(form, CommentForm)
        self.assertIsInstance(form.fields['text'], forms.fields.CharField)

    def test_add_comment(self):
        """Проверка создания комментария к посту."""
        form_data = {'text': 'Проверка создания комментария к посту.'}
        self.assertEqual(Comment.objects.count(), 0)
        self.assertRedirects(
            self.client.post(self.COMMENT_URL, data=form_data),
            self.POST_URL
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.all()[0]
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.author)
        self.assertEqual(comment.post, self.post)
