#!/bin/bash

python manage.py makemigrations
python manage.py migrate
# python manage.py load_all_data  #to do a load data of existing pics and posts
python manage.py collectstatic --no-input

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    python manage.py createsuperuser \
        --no-input \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

gunicorn yatube.wsgi:application --bind 0:8000