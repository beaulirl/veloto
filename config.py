import os
from dotenv import load_dotenv

load_dotenv()


def env(param, default=''):
    return os.environ.get(param, default)


# Strava data
CLIENT_ID = env('CLIENT_ID')
CLIENT_SECRET = env('CLIENT_SECRET')
STRAVA_BASE_URL = env('STRAVA_BASE_URL')
STRAVA_TOKEN = env('STRAVA_TOKEN')
STRAVA_VERIFY_TOKEN = env('VERIFY_TOKEN')

# Veloto data
CALLBACK_URL = env('CALLBACK_URL')

# Postgres data
POSTGRES_USER = env('POSTGRES_USER')
POSTGRES_PASSWORD = env('POSTGRES_PASSWORD')
POSTGRES_DB = env('POSTGRES_DB')

# APNS data
APNS_TOPIC = env('APNS_TOPIC', 'com.example.App')
APNS_KEY = env('APNS_KEY', 'key.pem')
