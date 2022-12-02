from datetime import datetime
from flask import Flask, make_response, jsonify, request
from db.models import Task, Tokens, User, StravaEvent
from config import STRAVA_VERIFY_TOKEN
from csv import reader

from db.config import session
from services.strava_service import StravaAPI
from services.notification_service import Notification

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://19201df010a347ff83bb60bdf224370b@o1132793.ingest.sentry.io/6178681",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

app = Flask(__name__)


strava_api = StravaAPI()
notification = Notification()


def get_default_tasks_list():
    default_tasks = []
    with open('default_tasks.csv', 'r') as default_tasks_file:
        csv_reader = reader(default_tasks_file)
        next(csv_reader)
        for task in csv_reader:
            default_tasks.append(task)
    return default_tasks


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/api/v1/athlete', methods=['GET'])
def get_authlete():
    user_id = request.args.get('user_id')
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return 'User not found', 404
    tasks = session.query(Task).filter_by(user_id=user.id).all()
    return jsonify({
        'user': user.id,
        'mileage': user.mileage,
        'tasks': [task.to_dict() for task in tasks]
    }), 200


@app.route('/api/v1/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    user_id = request.args.get('user_id')
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return 'User not found', 404
    task = session.query(Task).filter_by(id=task_id).first()
    if not task:
        return 'Task not found', 404
    if user.id != task.user_id:
        return 'Unauthorized', 403
    return jsonify({'task': task.to_dict()})


@app.route('/api/v1/tasks', methods=['POST'])
def create_task():
    task_name = request.json['name']
    task_repeat = request.json['every']
    task_comment = request.json['comment']
    user_id = request.args.get('user_id')
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return 'User not found', 404
    task = Task(name=task_name, every=task_repeat, comment=task_comment, user_id=user_id)
    task.remain = task_repeat
    session.add(task)
    session.commit()
    return jsonify(task.to_dict()), 201


@app.route('/api/v1/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    new_name = request.json.get('name')
    new_every = request.json.get('every')
    new_comment = request.json.get('comment')
    user_id = request.args.get('user_id')
    remain = request.json.get('remain')
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return 'User not found', 404
    task = session.query(Task).filter_by(id=task_id).first()
    if not task:
        return 'Task not found', 404
    if user.id != task.user_id:
        return 'Unauthorized', 403
    if new_name:
        task.name = new_name
    if new_every:
        diff = task.every - new_every
        task.remain -= diff
    if new_comment:
        task.comment = new_comment
    if remain:
        task.remain = remain
    session.add(task)
    session.commit()
    return jsonify(task.to_dict())


@app.route('/api/v1/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    user_id = request.args.get('user_id')
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return 'User not found', 404
    task = session.query(Task).filter_by(id=task_id).first()
    if not task:
        return 'Task not found', 404
    if user.id != task.user_id:
        return 'Unauthorized', 403
    session.delete(task)
    session.commit()
    return jsonify({'result': f'Task {task_id} was deleted'})


@app.route('/api/v1/tasks', methods=['GET'])
def get_tasks():
    user_id = request.args.get('user_id')
    tasks = session.query(Task).filter_by(user_id=user_id).all()
    return jsonify({'tasks': [task.to_dict() for task in tasks]})


def add_defaults_tasks_for_user(user):
    for value in get_default_tasks_list():
        session.add(Task(name=value[0], every=value[1], user_id=user.id, comment=value[2]))
    session.commit()


@app.route('/api/v1/users', methods=['DELETE'])
def delete_users():
    deleted = session.query(User).delete()
    session.commit()
    return jsonify({'result': f'Deleted {deleted} users'})


@app.route('/api/v1/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    session.query(User).filter_by(id=user_id).delete()
    session.commit()
    return jsonify({'result': f'Deleted user'})


@app.route('/api/v1/tasks/<int:task_id>/remain', methods=['PATCH'])
def patch_task_remain(task_id):
    user_id = request.args.get('user_id')
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return 'User not found', 404
    task = session.query(Task).filter_by(id=task_id).first()
    if not task:
        return 'Task not found', 404
    if user.id != task.user_id:
        return 'Unauthorized', 403
    task.remain = task.every
    session.commit()
    return jsonify({'result': f'Task {task_id} remain was set to 0'})


@app.route('/api/v1/users', methods=['POST'])
def create_user():
    access_token = request.json['access_token']
    refresh_token = request.json['refresh_token']
    strava_id = request.json['strava_id']
    apns_token = request.json['apns_token']
    user = session.query(User).filter_by(strava_id=strava_id).first()
    if not user:
        access_expires_at = datetime.fromtimestamp(int(request.json['access_expires_at']))
        token = Tokens(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_expires_at,
            apns_token=apns_token
        )
        session.add(token)
        session.commit()
        user = User(token_id=token.id, strava_id=strava_id)
        session.add(user)
        user_stats = strava_api.get_athlete_stats(user)
        add_defaults_tasks_for_user(user)
        user.mileage = user_stats['all_ride_totals']['distance'] if user_stats else 0
        session.commit()
    tasks = session.query(Task).filter_by(user_id=user.id).all()
    return jsonify({
        'user': user.id,
        'mileage': user.mileage,
        'tasks': [task.to_dict() for task in tasks]
    }), 201


@app.route('/callback_strava', methods=['GET'])
def get_strava_callback():
    hub_challenge = request.args.get('hub.challenge')
    hub_verify_token = request.args.get('hub.verify_token')
    if hub_verify_token == STRAVA_VERIFY_TOKEN:
        return jsonify({'hub.challenge': hub_challenge}), 200
    return 'Token is not verified', 403


@app.route('/debug-sentry')
def trigger_error():
    raise Exception('nnnn')
    # division_by_zero = 1 / 0


@app.route('/callback_strava', methods=['POST'])
def post_strava_callback():
    object_type = request.json.get('object_type')
    owner_id = request.json.get('owner_id')
    object_id = request.json.get('object_id')
    event_time = datetime.fromtimestamp(int(request.json['event_time']))
    if object_type == 'activity':
        user = session.query(User).filter_by(strava_id=int(owner_id)).first()
        if not user:
            return 'User not found', 404
        user_stats = strava_api.get_athlete_stats(user)
        total_distance = user_stats['all_ride_totals']['distance'] if user_stats else 0
        user.mileage = total_distance
        activity_info = strava_api.get_activity_info(object_id, user)
        recent_distance = activity_info['distance'] if activity_info else 0
        if recent_distance > 0:
            event = StravaEvent(user_id=user.id, distance=recent_distance, event_time=event_time)
            session.add(event)
            session.commit()
            notification.calculate_event_diff(user, recent_distance)
    return jsonify({'result': f'Strava callback finishes for strava_id {owner_id}'})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
