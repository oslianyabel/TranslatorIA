"""
Django settings for web_base project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
CORE_PARENT_DIR = BASE_DIR.parent  
sys.path.append(str(CORE_PARENT_DIR)) # src 
sys.path.append(str(CORE_PARENT_DIR.parent)) # TranlatorIA

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(CORE_PARENT_DIR.parent,"iconic-aloe-415006-16f2ae6eb878.json")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$%mpb=$v3i%bj@xlp2j*j5+k+b$moq#$yx9i!bd)nh1ti0g&wd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['173.208.156.35','173.247.225.140','yml-multilanguage.com','35.210.223.109','localhost',"127.0.0.1","108.181.193.15"]

CSRF_TRUSTED_ORIGINS = ['https://yml-multilanguage.com']

LOGIN_URL = "login"

LOGIN_REDIRECT_URL = "user_projects"
LOGOUT_REDIRECT_URL = "landing" 

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
# TODO generalize 
# SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = (f"http://127.0.0.1:8000/google-auth/complete/google-oauth2/")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'social_django',

    # 'allauth',
    # 'allauth.account',
    # 'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google', # https://www.section.io/engineering-education/django-google-oauth/
                                              # https://learnbatta.com/blog/signup-sign-in-using-google-to-django-application-8/
    # 'allauth.socialaccount.providers.facebook',
    # 'allauth.socialaccount.providers.twitter',
    # 'subscription',
    'accounts',
    'home',
    'video_translation',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'social_django.middleware.SocialAuthExceptionMiddleware',
    # 'allauth.account.middleware.AccountMiddleware',

    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'web_base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "web_base/templates/"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
            ],
        },
    },
]

WSGI_APPLICATION = 'web_base.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',

        'NAME': 'YML_Multilanguage',

        'USER': 'yml',

        'PASSWORD': 'Pppp54321!',

        'HOST': 'localhost', # needed if running MySQL in a virtual server or a separate server

        'PORT': '3307', # needed if running MySQL in a virtual server or a separate server
    }
}
AUTH_USER_MODEL = "accounts.UserBase"
AUTHENTICATION_BACKENDS = [
                "accounts.backends.EmailBackend",
                'social_core.backends.google.GoogleOAuth2',
                # "allauth.account.auth_backends.AuthenticationBackend"
                ]

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Email settings

EMAIL_USE_TLS = False    # Enables the use of a secure TLS (Transport Layer Security) connection when connecting to the email server.
                        # Set this to False if you want to use SSL (Secure Sockets Layer) instead

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' 
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-es.securemail.pro'  
#EMAIL_HOST_USER = 'apikey'  
EMAIL_HOST_USER = 'info@yml-multilanguage.com'   # https://pylessons.com/django-email-confirm
EMAIL_HOST_PASSWORD ='Pppp54321!#'  
EMAIL_PORT = 587 # 443      # Default port for TLS connections
# SENGRID 
# pip instal sendgrid 
EMAIL_KEY=os.getenv('EMAIL_KEY')
os.environ['SENDGRID_API_KEY'] = EMAIL_KEY

#EMAIL_USE_TLS =True         # REquired for smtp server
PASSWORD_RESET_TIMEOUT = 14400 # 4 hours

# Stripe  
    # https://justdjango.com/blog/django-stripe-payments-tutorial

STRIPE_PUBLIC_KEY = "pk_test_51OAIxhIUaaxT5wqlOXlVWPLUaXBD81vJTVUi1RbLrcYHLEuaZc"+\
                            "4WOwF9qSwxxNYTCsoRq30WAw8y0HfVHLx70bUY00B6G0Cgrq"
STRIPE_SECRET_KEY = "sk_test_51OAIxhIUaaxT5wqlvdgiWJ9gP99w930cpsCqCJjsRQ89vo58vfh"+\
                            "SpQ23YSyrS5CHyErPdTa0tsCYCjrtbEtFs9f400E7zXJ8H0"

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [('en','English'), ('es','Spanish')] # django-admin makemessages -l es      # django-admin compilemessages
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
# https://www.freecodecamp.org/news/localize-django-app/


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS  = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


MEDIA_ROOT = os.path.join(BASE_DIR,'media')
MEDIA_URL = 'media/'

VIDEOS_DIRECTORY = os.path.join(BASE_DIR, 'static','videos')

FREE_USERS_VIDEO_DUR_MS = 1 * 60 * 1000     # 1 minute
PAID_USERS_VIDEO_DUR_MS = 30 * 60 * 1000    # 30 minutes
FREE_USERS_STORAGE_MB = 150                 # 150MB
PAID_USERS_STORAGE_MB = 6 * 1024            # 6GB
FREE_USERS_TIME_VIDEO_DUR_RESET_DAYS = 30   # 30 days
PAID_USERS_TIME_VIDEO_DUR_RESET_DAYS = 30   # 30 days