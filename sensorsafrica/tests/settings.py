import os
from sensorsafrica.settings import *

import dj_database_url

DATABASE_URL = os.getenv("SENSORSAFRICA_TEST_DATABASE_URL")
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
    os.environ.setdefault("SENSORSAFRICA_IS_SQLITE", "false")
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    os.environ["SENSORSAFRICA_IS_SQLITE"] = "true"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
