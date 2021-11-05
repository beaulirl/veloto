import requests

from config import (
    CLIENT_ID,
    CLIENT_SECRET,
    STRAVA_BASE_URL,
    STRAVA_VERIFY_TOKEN,
    CALLBACK_URL
)
from app import token


class StravaAPI:

    def create_subscription(self):
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'callback_url': CALLBACK_URL,
            'verify_token': STRAVA_VERIFY_TOKEN
        }
        response = requests.post(
            f'{STRAVA_BASE_URL}/push_subscriptions',
            data,
            timeout=1
        )
        if response.status_code == 200:
            result = response.json()
            return result.get('id')
        return 'There was an error strava create subscription', response.status_code

    def get_athlete_stats(self, user):
        url = f'{STRAVA_BASE_URL}/athletes/{user.strava_id}/stats'
        if not token:
            return 0
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers, timeout=1)
        if response.status_code == 200:
            result = response.json()
            return result['recent_ride_totals']['distance']
        return 0

    def update_expired_token(self, refresh_token):
        url = f'{STRAVA_BASE_URL}/oauth/token'
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        response = requests.post(url, data, timeout=1)
        if response.status_code == 200:
            return response.json()
