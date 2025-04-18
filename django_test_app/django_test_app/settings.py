"""Django settings for django_test_app project."""

import os
from pathlib import Path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_dpvr*#hjgv)6v=potf%*+$na7_ck(*+^g08lw0^44zoo88)wb'  # noqa: S105

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Our custom checks:
    'django_test_migrations.contrib.django_checks.AutoNames',
    'django_test_migrations.contrib.django_checks.DatabaseConfiguration',
    # Custom:
    'main_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_test_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_test_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

_DATABASE_NAME = os.environ.get(
    'DJANGO_DATABASE_NAME',
    default=BASE_DIR.joinpath('db.sqlite3'),
)
DATABASES = {
    'default': {
        'ENGINE': os.environ.get(
            'DJANGO_DATABASE_ENGINE',
            default='django.db.backends.sqlite3',
        ),
        'USER': os.environ.get('DJANGO_DATABASE_USER', default=''),
        'PASSWORD': os.environ.get('DJANGO_DATABASE_PASSWORD', default=''),
        'NAME': _DATABASE_NAME,
        'PORT': os.environ.get('DJANGO_DATABASE_PORT', default=''),
        'HOST': os.environ.get('DJANGO_DATABASE_HOST', default=''),
        'TEST': {
            'NAME': (
                _DATABASE_NAME
                if _DATABASE_NAME.startswith('test_')
                else f'test_{_DATABASE_NAME}'
            ),
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
