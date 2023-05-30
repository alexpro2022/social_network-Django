import django
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        django.setup()
        ContentType.objects.all().delete()
