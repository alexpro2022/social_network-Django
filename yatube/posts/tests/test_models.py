from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User


USERNAME = 'author'
FIRST_NAME = 'Ivan'
LAST_NAME = 'Ivanov'
TITLE = 'Тестовая группа'
SLUG = 'Test-slug'
DESCRIPTION = 'Тестовое описание'
TEXT = 'Тестовый пост'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username=USERNAME,
            first_name=FIRST_NAME,
            last_name=LAST_NAME
        )
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION
        )
        cls.post = Post.objects.create(
            text=TEXT,
            author=cls.author,
            group=cls.group
        )

    def test_post_model_str_method(self):
        """Проверяем, что у модели поста корректно работает __str__."""
        self.assertEqual(
            str(self.post),
            Post.STR_METHOD_TEMPLATE.format(
                text=self.post.text,
                username=self.post.author.username,
                created=self.post.created,
                group=self.post.group,
            )
        )

    def test_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        self.assertEqual(Post._meta.verbose_name, 'Пост')
        self.assertEqual(Post._meta.verbose_name_plural, 'Посты')
        for field, expected_value in {
            'text': 'Текст',
            'created': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
        }.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        for field, expected_value in {
            'text': 'Введите или отредактируйте текст',
            'group': 'Группа, к которой будет относиться пост'
        }.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text,
                    expected_value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )

    def test_group_model_str_method(self):
        """Проверяем, что у модели группы корректно работает __str__."""
        self.assertEqual(str(self.group), self.group.title)

    def test_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        self.assertEqual(Group._meta.verbose_name, 'Группа')
        self.assertEqual(Group._meta.verbose_name_plural, 'Группы')
        for field, expected_value in {
            'title': 'Заголовок',
            'slug': 'Идентификатор',
            'description': 'Описание'
        }.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).verbose_name,
                    expected_value
                )


class CommentModelTest(TestCase):
    def test_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        self.assertEqual(Comment._meta.verbose_name, 'Комментарий')
        self.assertEqual(Comment._meta.verbose_name_plural, 'Комментарии')
        for field, expected_value in {
            'text': 'Текст комментария',
            'created': 'Дата создания',
            'author': 'Автор комментария',
            'post': 'Комментарий к посту'
        }.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        self.assertEqual(
            Comment._meta.get_field('text').help_text,
            'Введите текст комментария'
        )


class FollowModelTest(TestCase):
    def test_verbose_names(self):
        for field, expected_value in {
            'user': 'Подписанный пользователь',
            'author': 'Автор подписки'
        }.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Follow._meta.get_field(field).verbose_name,
                    expected_value
                )
