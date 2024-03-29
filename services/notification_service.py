from db.models import Notifications, Tokens, Task
from db.config import session
from apns2.client import APNsClient
from apns2.payload import Payload
from config import APNS_KEY, APNS_TOPIC


class Notification:

    def check_task_amount(self, task, user, recent_distance=0):
        task.remain -= recent_distance
        if task.remain <= 0:
            self.send_push_notification(task.comment, user)
            notification = Notifications(task_id=task.id, user_id=user.id)
            session.add(notification)
            task.remain = 0

        session.commit()


    def calculate_event_diff(self, user, recent_distance=0):
        tasks = session.query(Task).filter_by(user_id=user.id).all()
        for task in tasks:
            self.check_task_amount(task, user, recent_distance)

    def send_push_notification(self, comment, user):
        user_token = session.query(Tokens).filter_by(id=user.token_id).first()
        if not user_token and not user_token.apns_token:
            return
        print('Notification sending')
        # payload = Payload(alert=comment, sound="default", badge=1)
        # client = APNsClient(APNS_KEY, use_sandbox=False, use_alternative_port=False)
        # client.send_notification(user_token.apns_token, payload, APNS_TOPIC)
