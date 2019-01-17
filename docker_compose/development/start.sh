#!/bin/sh
python sensors_africa/manage.py migrate
python sensors_africa/manage.py runserver 0.0.0.0:8000