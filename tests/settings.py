import os.path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from siba import set_setting

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = []

MIDDLEWARE = []

USE_TZ = True
TIME_ZONE = "UTC"
SECRET_KEY = "foobar"


# translation configuration

set_setting("locales_path", os.path.join(BASE_DIR, "tests", "locales"))
set_setting("error_on_unknown_key", True)
set_setting("cache_locales", False)


