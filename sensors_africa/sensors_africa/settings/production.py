from .base import *

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sensorsaq',
        'USER': 'sensorsaq',
        'PASSWORD': 'sensorsaq',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}