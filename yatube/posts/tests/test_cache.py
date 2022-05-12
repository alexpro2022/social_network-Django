from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from ..models import Group, Post, User
from .utils import get_image


class CacheTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            first_name='Ivan',
            last_name='Ivanov'
        )
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        self.post = Post.objects.create(
            text='Тестовый пост кеширование',
            author=self.author,
            group=self.group,
            image=get_image('test_image.gif', 'image.gif')
        )

    def test_cache(self):
        """Проверяем, что после удаления записи контент главной страницы не меняется.
           После очистки кеша, контент главной страницы изменился."""
        INDEX_URL = reverse('posts:index')
        content_before_post_delete = self.client.get(INDEX_URL).content
        self.assertEqual(Post.objects.count(), 1)
        self.post.delete()
        self.assertEqual(Post.objects.count(), 0)
        content_after_post_delete = self.client.get(INDEX_URL).content
        self.assertEqual(content_before_post_delete, content_after_post_delete)
        cache.clear()
        content_after_cash_clear = self.client.get(INDEX_URL).content
        self.assertNotEqual(
            content_before_post_delete,
            content_after_cash_clear
        )
