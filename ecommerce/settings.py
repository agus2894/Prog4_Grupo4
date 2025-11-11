import os
from pathlib import Path
import environ
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env(
    DEBUG=(bool, True)
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


# SECRET_KEY from environment
SECRET_KEY = env("SECRET_KEY", default="dev-secret-no-usar-en-prod")

# DEBUG cuando no esté en Render (en Render setearás env var)
DEBUG = 'RENDER' not in os.environ

# ALLOWED_HOSTS: usa el host que Render provee en RENDER_EXTERNAL_HOSTNAME
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME]
else:
    # Para desarrollo local, priorizar localhost para OAuth
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "drf_yasg",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",  # Temporalmente desactivado
    "tienda",
    "usuarios",
    "simple_chat",
    'presupuesto',
    'telegram_bot',
    'analytics',  # Nueva app de IA y analytics
]

SITE_ID = 1


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# ============================================
# CONFIGURACIÓN DE ALLAUTH
# ============================================
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_UNIQUE_EMAIL = True

# Configuración de autenticación social
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_QUERY_EMAIL = True

# Configuración de campos de perfil social
# SOCIALACCOUNT_ADAPTER = 'usuarios.adapters.CustomSocialAccountAdapter'  # Temporalmente desactivado

# Forzar uso de localhost en desarrollo para OAuth
if DEBUG:
    # Asegurar que los callbacks de OAuth usen localhost
    USE_X_FORWARDED_HOST = False
    USE_X_FORWARDED_PORT = False


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

# Agregar middleware de localhost solo en desarrollo
if DEBUG:
    MIDDLEWARE.append("ecommerce.middleware.ForceLocalhostMiddleware")

MIDDLEWARE.extend([
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
])


ROOT_URLCONF = "ecommerce.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "ecommerce.wsgi.application"


# ============================================
# BASE DE DATOS
# ============================================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }



AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files — WhiteNoise
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


SOCIALACCOUNT_PROVIDERS = {
    # Configuración a través de la base de datos solamente
}


# ============================================
# CONFIGURACIÓN DE EMAIL
# ============================================
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@mercadito.com")
EMAIL_SUBJECT_PREFIX = "[Mercadito] "


# ============================================
# CONFIGURACIÓN DE TELEGRAM BOT
# ============================================
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="")

# ============================================
# CONFIGURACIÓN DE LOGGING
# ============================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

