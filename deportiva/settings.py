"""
Django settings for deportiva project.
"""

from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


# ========================
# SEGURIDAD
# ========================
SECRET_KEY = 'django-insecure-qy84mr=9km-rzwa3d%hc%rtoil=zxrrk&uto8qjix-gn0^_081'

# 🔥 PRODUCCIÓN (Railway)
DEBUG = True

ALLOWED_HOSTS = [
    '*'
]

CSRF_TRUSTED_ORIGINS = [
    'https://deportiva-production.up.railway.app',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True


# ========================
# APLICACIONES
# ========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del proyecto
    'usuarios',
    'canchas',
    'reservas',
]


# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Middleware personalizado
    'usuarios.middleware.RoleSecurityMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ========================
# URLS
# ========================
ROOT_URLCONF = 'deportiva.urls'


# ========================
# TEMPLATES
# ========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'deportiva.wsgi.application'


# ========================
# BASE DE DATOS
# ========================

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:

    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }

else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ========================
# VALIDACIÓN PASSWORD
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ========================
# USUARIO PERSONALIZADO
# ========================
AUTH_USER_MODEL = 'usuarios.Usuario'

AUTHENTICATION_BACKENDS = [
    'usuarios.backends.EmailOrUsernameBackend',
]


# ========================
# INTERNACIONALIZACIÓN
# ========================
LANGUAGE_CODE = 'es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ========================
# ARCHIVOS ESTÁTICOS
# ========================
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# ========================
# LOGIN / LOGOUT
# ========================
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/canchas/home/'
LOGOUT_REDIRECT_URL = '/'


# ========================
# EMAIL
# ========================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ========================
# MEDIA
# ========================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'