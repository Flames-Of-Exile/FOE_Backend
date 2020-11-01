import functools

from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import disconnect, emit
from jwt.exceptions import DecodeError

from models import Campaign, User
from app import socketio


def requires_authentication(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        refresh_token = request.cookies.get('refresh_token')
        try:
            user = User.query.get(decode_token(refresh_token)['identity']['id'])
        except DecodeError:
            disconnect()
            return False
        if (not user.is_active or not user.guild.is_active or not user.discord_confirmed
                or user.role not in [User.Role.VERIFIED, User.Role.ADMIN]):
            disconnect()
            return False
        return function(*args, **kwargs)
    return wrapper


@requires_authentication
@socketio.on('connect')
def on_connect():
    pass


@requires_authentication
@socketio.on('campaign-update')
def handle_campaign_update():
    data = [campaign.to_dict() for campaign in Campaign.query.filter_by(is_archived=False)
                    .order_by(Campaign.is_default.desc(), Campaign.id.desc()).all()]
    emit('campaign-update', data, broadcast=True)
