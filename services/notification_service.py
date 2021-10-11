from db.models import Notifications
from db.config import session


class Notification:

    def calculate_event_diff(self, user, diff_distance):
        for task in user.tasks:
            old_notification = session.query(Notifications).filter_by(task_id=task.id, user_id=user.id).first()
            diff = old_notification.diff if old_notification else 0
            amount = diff_distance + diff
            if amount > task.every:
                self.send_push_notification()
                new_diff = amount - task.every
            else:
                new_diff = diff_distance + diff

            if old_notification:
                old_notification.diff = new_diff
            else:
                notification = Notifications(task_id=task.id, user_id=user.id, diff=new_diff)
                session.add(notification)
            session.commit()

    def send_push_notification(self):
        print('push notification sent')
