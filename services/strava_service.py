import requests
from config import (
    CLIENT_ID,
    CLIENT_SECRET,
    STRAVA_BASE_URL,
    STRAVA_TOKEN,
    STRAVA_VERIFY_TOKEN,
    CALLBACK_URL
)


class StravaAPI:

    def create_subscription(self):
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'callback_url': CALLBACK_URL,
            'verify_token': STRAVA_VERIFY_TOKEN
        }
        response = requests.post(f'{STRAVA_BASE_URL}/push_subscriptions', data, timeout=1)
        if response.status_code == 200:
            result = response.json()
            return result.get('id')

    def get_athlete_stats(self, user_id):
        url = f'{STRAVA_BASE_URL}/athletes/{user_id}/stats'
        headers = {'Authorization': STRAVA_TOKEN}
        response = requests.get(url, headers, timeout=1)
        if response.status_code == 200:
            result = response.json()
            return result['recent_ride_totals']['distance']
