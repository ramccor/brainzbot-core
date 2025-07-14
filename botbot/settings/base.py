import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

#==============================================================================
# Generic Django project settings
#==============================================================================

DEBUG = os.environ.get('DEBUG', 'True')

SITE_ID = 1
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'UTC'
USE_TZ = True
USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', 'English'),
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ['SECRET_KEY']
INSTALLED_APPS = (
    'django_jinja',  # Must be before django.contrib.staticfiles

    'botbot.apps.bots',
    'botbot.apps.logs',
    'botbot.apps.plugins',
    'botbot.core',

    'whitenoise.runserver_nostatic',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'bootstrap3',
)

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

#==============================================================================
# Project URLS and media settings
#==============================================================================

ROOT_URLCONF = 'botbot.urls'

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

DATABASES = {'default': dj_database_url.config(env='STORAGE_URL')}
# Reuse database connections
DATABASES['default'].update({
    'CONN_MAX_AGE': None,
    'ATOMIC_REQUESTS': True,
})

#==============================================================================
# Templates
#==============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'OPTIONS': {
            'environment': 'botbot.jinja2.environment',
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
            'debug': DEBUG,
        },
    },
]
#==============================================================================
# Middleware
#==============================================================================
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'botbot.core.middleware.TimezoneMiddleware',
]

# Bootstrap 3 settings
BOOTSTRAP3 = {
    'jquery_url': '//code.jquery.com/jquery-3.6.0.min.js',
    'base_url': '//maxcdn.bootstrapcdn.com/bootstrap/3.4.1/',
    'include_jquery': True,
    'javascript_url': '//maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js',
    'css_url': '//maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css',
    'theme_url': None,
    'javascript_in_head': False,
    'include_clearfix': True,
    'use_required_attribute': True,
    'set_placeholder': True,
    'required_css_class': 'required',
    'error_css_class': 'has-error',
    'success_css_class': 'has-success',
    'formset_renderers': {
        'default': 'bootstrap3.renderers.FormsetRenderer',
    },
    'form_renderers': {
        'default': 'bootstrap3.renderers.FormRenderer',
    },
    'field_renderers': {
        'default': 'bootstrap3.renderers.FieldRenderer',
        'inline': 'bootstrap3.renderers.InlineFieldRenderer',
    },
}

#==============================================================================
# Auth / security
#============================================================================

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

#==============================================================================
# Logger project settings
#==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': []
        }
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'botbot': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

#=============================================================================
# Cache
#=============================================================================
DEFAULT_CACHE = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'botbot',
}

CACHES = {
    'default': DEFAULT_CACHE
}

CACHE_MIDDLEWARE_SECONDS = 600  # Unit is second

#==============================================================================
# Miscellaneous project settings
#==============================================================================

# Above this many users is considered a big channel, display is different
BIG_CHANNEL = 25
# Nicks requested to be excluded from logging
EXCLUDE_NICKS = os.environ.get('EXCLUDE_NICKS', '').split(',')
if EXCLUDE_NICKS == ['']:
    EXCLUDE_NICKS = []

REDIS_PLUGIN_QUEUE_URL = os.environ.get('REDIS_PLUGIN_QUEUE_URL')
REDIS_PLUGIN_STORAGE_URL = os.environ.get('REDIS_PLUGIN_STORAGE_URL')

COMMAND_PREFIX = os.environ.get('COMMAND_PREFIX')

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

import warnings
warnings.filterwarnings("error")
