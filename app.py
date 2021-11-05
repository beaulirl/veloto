import datetime
from flask import Flask, make_response, jsonify, request
from db.models import Task, Tokens, User, StravaEvent
from config import STRAVA_VERIFY_TOKEN, TOKEN_ID

app = Flask(__name__)

from db.config import session
from services.strava_service import StravaAPI
from services.notification_service import Notification

strava_api = StravaAPI()
notification = Notification()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@property
def token():
    general_token = session.query(Tokens).filter_by(id=TOKEN_ID).first()
    if general_token.timestamp < datetime.datetime.now().timestamp():
        token_info = strava_api.update_expired_token(general_token.refresh_token)

        if not token_info:
            return

        general_token.access_token = token_info.get('access_token')
        general_token.refresh_token = token_info.get('refresh_token')
        general_token.timestamp = token_info.get('expires_at')
        session.commit()

    return general_token.access_token


@app.route('/api/v1/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    user_id = request.args.get('user_id')
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return 'User not found', 404
    task = session.query(Task).filter_by(id=task_id).first()
    if task not in user.tasks:
        return 'Unauthorized', 403
    return jsonify({'task': task.to_dict()})


@app.route('/api/v1/tasks', methods=['POST'])
def create_task():
    task_name = request.form['name']
    task_repeat = request.form['every']
    task_comment = request.form['comment']
    user_id = request.args.get('user_id')
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return 'User not found', 404
    task = Task(name=task_name, every=task_repeat, comment=task_comment)
    session.add(task)
    user.tasks.append(task)
    session.commit()
    return jsonify({'task': task.id}), 201


@app.route('/api/v1/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    new_name = request.form.get('name')
    new_every = request.form.get('every')
    new_comment = request.form.get('comment')
    user_id = request.args.get('user_id')
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return 'User not found', 404
    task = session.query(Task).filter_by(id=task_id).first()
    if task not in user.tasks:
        return 'Unauthorized', 403
    if new_name:
        task.name = new_name
    if new_every:
        task.every = new_every
    if new_comment:
        task.comment = new_comment
    session.add(task)
    session.commit()
    return jsonify({'task': task.id})


@app.route('/api/v1/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    user_id = request.args.get('user_id')
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return 'User not found', 404
    task = session.query(Task).filter_by(id=task_id).first()
    if task not in user.tasks:
        return 'Unauthorized', 403
    session.delete(task)
    session.commit()
    return jsonify({'result': f'Task {task_id} was deleted'})


@app.route('/api/v1/tasks', methods=['GET'])
def get_tasks():
    user_id = request.args.get('user_id')
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return 'User not found', 404
    return jsonify({'tasks': [task.to_dict() for task in user.tasks]})


@app.route('/api/v1/users', methods=['POST'])
def create_user():
    access_token = request.form['access_token']
    refresh_token = request.form['refresh_token']
    strava_id = request.form['strava_id']
    apns_token = request.form['apns_token']
    mileage = request.form['mileage']
    access_expires_at = datetime.datetime.fromtimestamp(int(request.form['access_expires_at']))
    token = Tokens(
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_at=access_expires_at,
        apns_token=apns_token
    )
    session.add(token)
    session.commit()
    user = User(token=token.id, strava_id=strava_id, mileage=mileage)
    session.add(user)
    session.commit()
    return jsonify({'user': user.id}), 201


@app.route('/callback_strava', methods=['GET'])
def get_strava_callback():
    hub_challenge = request.args.get('hub.challenge')
    hub_verify_token = request.args.get('hub.verify_token')
    if hub_verify_token == STRAVA_VERIFY_TOKEN:
        return jsonify({'hub.challenge': hub_challenge}), 200
    return 'Token is not verified', 403


@app.route('/callback_strava', methods=['POST'])
def post_strava_callback():
    object_type = request.form.get('object_type')
    owner_id = request.form.get('owner_id')
    event_time = datetime.datetime.fromtimestamp(int(request.form['event_time']))
    if object_type == 'activity':
        user = session.query(User).filter_by(strava_id=int(owner_id)).first()
        if not user:
            return 'User not found', 404
        distance = strava_api.get_athlete_stats(user)
        user_distance = user.mileage if user.mileage else 0
        diff_distance = distance - user_distance
        if diff_distance > 0:
            event = StravaEvent(user_id=user.id, event_km=diff_distance, event_time=event_time)
            session.add(event)
            session.commit()
            notification.calculate_event_diff(user, diff_distance)
        return jsonify({'user': user.id}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
