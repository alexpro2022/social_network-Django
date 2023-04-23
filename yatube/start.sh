#!/bin/bash

python manage.py makemigrations
python manage.py migrate
# python manage.py load_all_data  #to do a load data of existing pics and posts
python manage.py collectstatic --no-input
gunicorn yatube.wsgi:application --bind 0:8000