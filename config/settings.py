import os
from pathlib import Path
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env', override=False)
def flag(name, default=False):
    return os.getenv(name, str(default)).lower() in {'1','true','yes'}
def items(name, default=''):
    return [s.strip() for s in os.getenv(name, default).split(',') if s.strip()]
DEBUG = flag('DEBUG')
SECRET_KEY = os.getenv('SECRET_KEY', '')
if len(SECRET_KEY) < 50 or SECRET_KEY.startswith('REPLACE_'):
    raise ImproperlyConfigured('Set a unique SECRET_KEY of at least 50 characters. Run python scripts/setup_local.py for development.')
ALLOWED_HOSTS = items('ALLOWED_HOSTS', 'localhost,127.0.0.1' if DEBUG else '')
if not DEBUG and (not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS):
    raise ImproperlyConfigured('Production requires explicit ALLOWED_HOSTS.')
INSTALLED_APPS = ['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','django.contrib.sitemaps','axes','garden']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware','axes.middleware.AxesMiddleware','garden.middleware.SiteMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages','garden.context.site_context']}}]
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'
if os.getenv('DB_ENGINE') == 'postgres':
    DATABASES = {'default':{'ENGINE':'django.db.backends.postgresql','NAME':os.environ['DB_NAME'],'USER':os.environ['DB_USER'],'PASSWORD':os.environ['DB_PASSWORD'],'HOST':os.getenv('DB_HOST','127.0.0.1'),'PORT':os.getenv('DB_PORT','5432'),'CONN_MAX_AGE':60,'OPTIONS':{'sslmode':os.getenv('DB_SSLMODE','prefer')}}}
else:
    DATABASES = {'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3','OPTIONS':{'timeout':20}}}
AUTH_PASSWORD_VALIDATORS = [{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':12}},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
AUTHENTICATION_BACKENDS = ['axes.backends.AxesStandaloneBackend','django.contrib.auth.backends.ModelBackend']
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address']
AXES_RESET_ON_SUCCESS = True
AXES_ENABLE_ACCESS_FAILURE_LOG = False
AXES_CLIENT_IP_CALLABLE = 'garden.security.client_ip'
AXES_LOCKOUT_TEMPLATE = 'registration/locked.html'
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR/'staticfiles'
STATICFILES_DIRS = [BASE_DIR/'static']
STORAGES = {'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR/'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/my-garden/'
LOGOUT_REDIRECT_URL = '/'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_AGE = 60*60*24*7
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = flag('HSTS_INCLUDE_SUBDOMAINS')
SECURE_HSTS_PRELOAD = flag('HSTS_PRELOAD')
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'
CSRF_TRUSTED_ORIGINS = items('CSRF_TRUSTED_ORIGINS')
# Enable ONLY behind a proxy you control which strips incoming forwarded headers.
if flag('TRUST_PROXY_HTTPS'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO','https')
DATA_UPLOAD_MAX_MEMORY_SIZE = 5*1024*1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 3*1024*1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST','')
EMAIL_PORT = int(os.getenv('EMAIL_PORT','587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER','')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD','')
EMAIL_USE_TLS = flag('EMAIL_USE_TLS', True)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL','noreply@localhost')
EMAIL_TIMEOUT = 10
PASSWORD_RESET_TIMEOUT = 3600
WEATHER_ENABLED = flag('WEATHER_ENABLED')
CACHES = {'default':{'BACKEND':'django.core.cache.backends.db.DatabaseCache','LOCATION':'garden_cache','TIMEOUT':1800,'OPTIONS':{'MAX_ENTRIES':2000}}}
SITE_URL = os.getenv('SITE_URL','http://127.0.0.1:8000').rstrip('/')
LOGGING = {'version':1,'disable_existing_loggers':False,'handlers':{'console':{'class':'logging.StreamHandler'}},'root':{'handlers':['console'],'level':'WARNING'}}

TRUSTED_PROXY_IPS = items('TRUSTED_PROXY_IPS')
