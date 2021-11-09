import datetime
import requests

from config import (
    CLIENT_ID,
    CLIENT_SECRET,
    STRAVA_BASE_URL,
    STRAVA_VERIFY_TOKEN,
    CALLBACK_URL
)
from db.config import session
from db.models import Tokens


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
        if response.status_code == 201:
            result = response.json()
            return result.get('id')
        return 'There was an error strava create subscription', response.status_code

    def get_athlete_stats(self, user):
        url = f'{STRAVA_BASE_URL}/athletes/{user.strava_id}/stats'
        token = self.get_user_token(user)
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
        if response.status_code == 201:
            return response.json()

    def get_user_token(self, user):
        general_token = session.query(Tokens).filter_by(id=user.token).first()
        if general_token.access_expires_at < datetime.datetime.now():
            token_info = self.update_expired_token(general_token.refresh_token)

            if not token_info:
                return

            general_token.access_token = token_info.get('access_token')
            general_token.refresh_token = token_info.get('refresh_token')
            general_token.timestamp = token_info.get('expires_at')
            session.commit()

        return general_token.access_token
