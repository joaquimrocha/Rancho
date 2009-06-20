# -*- coding: utf-8 -*-

# Django settings for rancho project.

import os

LOCAL_DEV = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DJANGO_PROJECT = 'rancho'
DJANGO_SETTINGS_MODULE = 'rancho.settings'

DIRNAME = os.path.abspath(os.path.dirname(__file__).decode('utf-8'))

ADMINS = (
    ('', ''),
)

MANAGERS = ADMINS

SEARCH_ENGINE=''               # Use 'mysql' or 'postgresql' according to the database you wish to use.

DATABASE_ENGINE = ''           # Use 'postgresql' or 'mysql' according to the database you wish to use.
DATABASE_NAME = ''             # The database name.
DATABASE_USER = ''             # The user name to access the database.
DATABASE_PASSWORD = ''         # The user password to access the database.
DATABASE_HOST = ''             # Set to empty string for localhost or otherwise use the host you wish.
DATABASE_PORT = ''             # Set to empty string for default or otherwise set the port you wish.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Lisbon'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(DIRNAME, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

# Make this unique, and don't share it with anybody.
# SECRET_KEY = ''

# Email stuffs
DEFAULT_FROM_EMAIL = ''        # For example no-reply@YOUREMAILSERVER.COM
EMAIL_HOST = ''                # For example smtp.YOUREMAILSERVER.COM
EMAIL_HOST_USER = ''           # For example YOURNAME@YOUREMAILSERVER.COM
EMAIL_HOST_PASSWORD = ''       # Your email password
EMAIL_USE_TLS = True

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (    
    'lib.middleware.Custom403Middleware',                    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'lib.middleware.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',    
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'rancho.lib.context_processors.rancho',
)


ROOT_URLCONF = 'rancho.urls'

TEMPLATE_DIRS = (
    os.path.join(DIRNAME, "templates"),
)

#Auth profile model
AUTH_PROFILE_MODULE = 'user.UserProfile'

LOGIN_URL = '/auth/login'
LOGIN_REDIRECT_URL = '/dashboard'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',

    'pagination',
    'tagging',
    'notification',    
    'mailer',
    'granular_permissions',
    'tinymce',
    'timezones',
    'django_evolution',

    'rancho.user',
    'rancho.project',
    'rancho.message',    
    'rancho.company',
    'rancho.file',
    'rancho.milestone',    
    'rancho.lib',
    'rancho.wikiboard',    
    'rancho.todo',
    'rancho.cal',    
    'rancho.chat',
    
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# COMPANY STUFF
UPLOAD_DIR = 'upload/'
COMPANY_DIR = 'company/'
COMPANY_LOGO_SIZE = (250, 80)
PROJECT_DIR = 'project/'
PROJECT_LOGO_SIZE = (250, 100)
PROJECT_PIC_MAX_SIZE = 1024**3 # 1 Mb
PEOPLE_DIR = 'people/'
PROFILE_PICTURE_SIZE = (48, 48)
PROFILE_LARGE_PICTURE_SIZE = (450, 500)

#how to send a file back to the user (django builtin code is very bad)
#use of the following: apache-modsendfile , django
HOW_SEND_FILE='django' 

# LANGUAGES
LANGUAGES = (('en-us', u'English'), ('pt-pt', u'Português'), ('es-es', u'Español'),)
