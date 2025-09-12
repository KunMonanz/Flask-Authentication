from flask_jwt_extended import get_jwt_identity

from models import User, Task


def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    return user


def get_current_user():
    username = get_jwt_identity()
    return User.query.filter_by(username=username).first()


def get_user_task(task_id, user_id):
    return Task.query.filter_by(id=task_id, user_id=user_id).first()
