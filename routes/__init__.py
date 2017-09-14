from flask import session

from models.user import User
import datetime


def current_user():
    uid = session.get('user_id', '')
    u = User.find_by(id=uid)
    if u is None:
        u = User.find_by(username='guest')
    return u
