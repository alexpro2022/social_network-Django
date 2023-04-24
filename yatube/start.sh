#!/bin/bash

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    python manage.py createsuperuser \
        --no-input \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

export DJANGO_SETTINGS_MODULE=yatube.settings
python << END
import django
django.setup()
from django.contrib.contenttypes.models import ContentType
ContentType.objects.all().delete()
END
python manage.py loaddata dump.json

gunicorn yatube.wsgi:application --bind 0:8000
