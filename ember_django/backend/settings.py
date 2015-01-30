#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Django settings for ember_django project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
'''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'some_key'

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*',]


# Application definition
# rest_framework_ember adapter is added for ember-django communication

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'backend',
    'rest_framework',
    'rest_framework_ember',
    'rest_framework.authtoken',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'backend.urls'

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'escience',
        'USER': 'developer',
        'PASSWORD': 'escience',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# rest_framework settings for the rest_framework_ember
# https://github.com/ngenworks/rest_framework_ember

REST_FRAMEWORK = {
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100,
    'DEFAULT_PAGINATION_SERIALIZER_CLASS':
        'rest_framework_ember.pagination.EmberPaginationSerializer',
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework_ember.parsers.EmberJSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework_ember.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [],
}

# By default Django expects a trailing slash on urls and will 301 redirect
# any requests lacking a trailing slash.
# This is why we set APPEND_SLASH = False.

APPEND_SLASH = False

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
if DEBUG:
    STATIC_PATH = os.path.join(BASE_DIR, 'frontend/app')
    STATIC_URL = '/frontend/app/'   
    STATICFILES_DIRS = (
        STATIC_PATH,
    )
    TEMPLATE_DIRS = (
        os.path.join(BASE_DIR, 'frontend/app'),
    )
else:
    PROJECT_DEFAULT_STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../frontend/app')
    STATIC_PATH = os.path.join(BASE_DIR, 'static')
    STATIC_URL = '/static/'
    STATICFILES_DIRS = (
        PROJECT_DEFAULT_STATIC_DIR,
    )
    TEMPLATE_DIRS = (
        os.path.join(BASE_DIR, 'static'),
    )
    # EXTRA FOR NGINX
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/home/developer/logs/debug.log',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }
