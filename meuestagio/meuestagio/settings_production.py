from settings import *

DEBUG = False
ALLOWED_HOSTS = '*'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '{{ DB_NAME }}',
        'USER': '{{ DB_USER }}',
        'PASSWORD': '{{ DB_PASSWORD }}',
        'HOST': '',
        'PORT': '',
    }
}
