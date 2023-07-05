from .settings import *

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3"}
}

AUTH_PASSWORD_VALIDATORS = []

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
}

# LOGGING["loggers"]["django.db"] = {"level": "DEBUG"}
