from django.test import Client, TestCase
from django.urls import reverse


class AboutURLsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_templates_relations(self):
        urls_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in urls_templates.items():
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, 200, f'ERROR: {url}')
            self.assertTemplateUsed(response, template, f'ERROR: {template}')


class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_names_templates_relations(self):
        names_templates = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for name, template in names_templates.items():
            response = self.guest_client.get(reverse(name))
            with self.subTest(name=name):
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)
