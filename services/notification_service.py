from db.models import Notifications, Tokens
from db.config import session
from apns2.client import APNsClient
from apns2.payload import Payload
from config import APNS_KEY, APNS_TOPIC


class Notification:

    def calculate_event_diff(self, user, diff_distance):
        for task in user.tasks:
            old_notification = session.query(Notifications).filter_by(task_id=task.id, user_id=user.id).first()
            diff = old_notification.diff if old_notification else 0
            amount = diff_distance + diff
            if amount > task.every:
                self.send_push_notification(task.comment, user)
                new_diff = amount - task.every
            else:
                new_diff = diff_distance + diff

            if old_notification:
                old_notification.diff = new_diff
            else:
                notification = Notifications(task_id=task.id, user_id=user.id, diff=new_diff)
                session.add(notification)
            session.commit()

    def send_push_notification(self, comment, user):
        user_token = session.query(Tokens).filter_by(id=user.token_id).first()
        if not user_token and not user_token.apns_token:
            return
        payload = Payload(alert=comment, sound="default", badge=1)
        client = APNsClient(APNS_KEY, use_sandbox=False, use_alternative_port=False)
        client.send_notification(user_token.apns_token, payload, APNS_TOPIC)
