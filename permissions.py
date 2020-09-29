from functools import wraps

from flask import Response
from flask_jwt_extended import get_jwt_identity

from models import db, User

def is_administrator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity()['id'])
        if (user.role != User.Role.ADMIN.value):
            return Response('requires administrator account', status=403)
        return func(*args, **kwargs)
    return wrapper

def is_member(func, **kwargs):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity()['id'])
        if (user.role in [User.Role.MEMBER.value, User.Role.ADMIN.value]):
            return Response('requires member account', status=403)
        return func(*args, **kwargs)
    return wrapper