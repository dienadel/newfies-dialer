import os

#DEBUG
#=====
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

#TODO : Installation script should ask the timezone
TIME_ZONE = 'Europe/Madrid'

APPLICATION_DIR = os.path.dirname(globals()['__file__'])

#DATABASE SETTINGS
#=================
DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2','postgresql','mysql','sqlite3','oracle'
        'ENGINE': 'django.db.backends.sqlite3',
        # Or path to database file if using sqlite3.
        'NAME': APPLICATION_DIR + '/database/test.db',
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost.
                                         # Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default.
                                         # Not used with sqlite3.
        'OPTIONS': {
           'init_command': 'SET storage_engine=INNODB',
        }
    }
}


#CELERY SETTINGS
#===============
CARROT_BACKEND = 'redis'
BROKER_HOST = 'localhost'  # Maps to redis host.
BROKER_PORT = 6379         # Maps to redis port.
BROKER_VHOST = 0        # Maps to database number.

CELERY_RESULT_BACKEND = 'redis'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
#REDIS_CONNECT_RETRY = True


#EMAIL BACKEND
#=============
# Use only in Debug mode. Not in production
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


#PLIVO
#=====
PLIVO_DEFAULT_ANSWER_URL = 'http://SERVER_IP_PORT/api/v1/answercall/'
PLIVO_DEFAULT_HANGUP_URL = 'http://SERVER_IP_PORT/api/v1/hangupcall/'
PLIVO_DEFAULT_DIALCALLBACK_URL = 'http://SERVER_IP_PORT/api/v1/dialcallback/'

# ADD 'dummy','plivo','twilio'
NEWFIES_DIALER_ENGINE = 'dummy'

API_ALLOWED_IP = [
            '127.0.0.1', 
            'localhost', 
            #'SERVER_IP',
                ]
