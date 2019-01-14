#!/bin/sh

creatdb sensorsafrica

python manage.py migrate
python manage.py runserver 0.0.0.0:8000