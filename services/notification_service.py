from db.models import Notifications, Tokens, Task
from db.config import session
from apns2.client import APNsClient
from apns2.payload import Payload
from config import APNS_KEY, APNS_TOPIC


class Notification:

    def calculate_event_diff(self, user_id, diff_distance=0):
        tasks = session.query(Task).filter_by(user_id=user_id).all()
        for task in tasks:
            amount = diff_distance + task.remain
            if amount >= task.every:
                self.send_push_notification(task.comment, user_id)
                notification = Notifications(task_id=task.id, user_id=user_id)
                session.add(notification)
                new_diff = amount - task.every
            else:
                new_diff = amount
            task.remain = new_diff

            session.commit()

    def send_push_notification(self, comment, user):
        user_token = session.query(Tokens).filter_by(id=user.token).first()
        if not user_token and not user_token.apns_token:
            return
        print('Notification sending')
        # payload = Payload(alert=comment, sound="default", badge=1)
        # client = APNsClient(APNS_KEY, use_sandbox=False, use_alternative_port=False)
        # client.send_notification(user_token.apns_token, payload, APNS_TOPIC)
