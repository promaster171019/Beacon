import os

print('* Load local settings...')
GOOGLE_APPLICATION_CREDENTIALS = {
  "web": {
    "client_id": "56343814273-ji6m9jpn1h7dl4od07k25q72cthvs29f.apps.googleusercontent.com",
    "project_id": "beacon-dj",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "RwK_KSHn1TsfbVUjoomsms6A",
    "redirect_uris": [
      "http://localhost:8000"
    ],
    "javascript_origins": [
      "http://localhost:8000"
    ]
  }
}

SITE_HOST = 'localhost:8001'

# [START db_setup]
if False:
    # Running on production App Engine, so connect to Google Cloud SQL using
    # the unix socket at /cloudsql/<your-cloudsql-connection string>
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': '',
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            'PORT': ''
        }
    }
else:
    # Running locally so connect to either a local MySQL instance or connect to
    # Cloud SQL via the proxy. To start the proxy via command line:
    #
    #     $ cloud_sql_proxy -instances=[INSTANCE_CONNECTION_NAME]=tcp:3306
    #
    # See https://cloud.google.com/sql/docs/mysql-connect-proxy
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'beacon_db_local',
            'USER': 'postgres',
            'PASSWORD': 'root',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }
# [END db_setup]

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'creds_gcalendar.json'
APPLICATION_NAME = 'Beacon Google Calendar API'

# Email settings
if True:
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_SSL = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 465
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 465
    EMAIL_HOST_USER = 'example@mail.ru'

DEFAULT_FROM_EMAIL = ''

# storage settings
GS_BUCKET_NAME = 'django-beacon-stage'
GS_PROJECT_ID = 'beacon-158615'

STATIC_ROOT = 'https://storage.googleapis.com/django-beacon-stage/static/'
STATIC_URL = 'https://storage.googleapis.com/django-beacon-stage/static/'

MEDIA_ROOT = 'https://storage.googleapis.com/django-beacon-stage/media/'
MEDIA_URL = 'https://storage.googleapis.com/django-beacon-stage/media/'