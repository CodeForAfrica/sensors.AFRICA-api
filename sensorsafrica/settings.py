"""
Django settings for sensorsafrica project.

Generated by 'django-admin startproject' using Django 1.10.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SENSORSAFRICA_SECRET_KEY", "-kc8keig#xrdhi1l$rrj&s*s@3pz*4he)8u8h^w$2-_4y6@z3g"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("SENSORSAFRICA_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv("SENSORSAFRICA_ALLOWED_HOSTS", "*").split(",")

CORS_ORIGIN_ALLOW_ALL = True

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_filters",
    # Django Rest Framework
    "rest_framework",
    "rest_framework.authtoken",
    # Feinstaub
    "feinstaub",
    "feinstaub.main",
    "feinstaub.sensors",
    # API
    "sensorsafrica",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sensorsafrica.urls"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": DEBUG,
        },
    }
]

WSGI_APPLICATION = "sensorsafrica.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASE_URL = os.getenv(
    "SENSORSAFRICA_DATABASE_URL",
    "postgres://sensorsafrica:sensorsafrica@localhost:5432/sensorsafrica",
)
DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static")


# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Recheck the filesystem to see if any files have changed before responding.
WHITENOISE_AUTOREFRESH = True

# Celery Broker
CELERY_BROKER_URL = os.environ.get(
    "SENSORSAFRICA_RABBITMQ_URL", "amqp://sensorsafrica:sensorsafrica@localhost//"
)
CELERY_IGNORE_RESULT = True

CELERY_BEAT_SCHEDULE = {
    "statistics-task": {
        "task": "sensorsafrica.tasks.calculate_data_statistics",
        "schedule": crontab(hour="*", minute=0),
    },
    "archive-task": {
        "task": "sensorsafrica.tasks.archive_data",
        "schedule": crontab(hour="*", minute=0),
    },
    "cache-lastactive-nodes-task": {
        "task": "sensorsafrica.tasks.cache_lastactive_nodes",
        "schedule": crontab(minute="*/5"),
    },
    "cache-static-json-data": {
        "task": "sensorsafrica.tasks.cache_static_json_data",
        "schedule": crontab(minute="*/5"),
    },
    "cache-static-json-data-1h-24h": {
        "task": "sensorsafrica.tasks.cache_static_json_data_1h_24h",
        "schedule": crontab(hour="*", minute=0),
    },
}


# Sentry
sentry_sdk.init(
    os.environ.get("SENSORSAFRICA_SENTRY_DSN", ""),
    integrations=[CeleryIntegration(), DjangoIntegration()],
)


# Put fenstaub migrations into sensorsafrica
MIGRATION_MODULES = {
    "sensors": "sensorsafrica.openstuttgart.feinstaub.sensors.migrations"
}

NETWORKS_OWNER = os.getenv("NETWORKS_OWNER")
