from .settings import *

INSTALLED_APPS += [
    "django_extensions"
]

AUTH_PASSWORD_VALIDATORS = []

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
}

# LOGGING["loggers"]["django.db"] = {"level": "DEBUG"}
