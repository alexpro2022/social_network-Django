from django.test import TestCase
from django.urls import reverse
from posts.urls import app_name

SLUG = 'Test-slug'
USERNAME = 'author'
POST_ID = 1
CASES = (
    ('/', 'index', []),
    ('/create/', 'post_create', []),
    (f'/group/{SLUG}/', 'group_list', [SLUG]),
    (f'/profile/{USERNAME}/', 'profile', [USERNAME]),
    (f'/posts/{POST_ID}/', 'post_detail', [POST_ID]),
    (f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]),
    (f'/posts/{POST_ID}/comment/', 'add_comment', [POST_ID]),
    ('/follow/', 'follow_index', []),
    (f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]),
    (f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME])
)


class RoutesTest(TestCase):
    def test_url_corresponds_with_namespace_name(self):
        """Проверка соответствия урл его namespace:name."""
        for url, name, args in CASES:
            with self.subTest(url=url):
                self.assertEqual(url, reverse(f'{app_name}:{name}', args=args))
