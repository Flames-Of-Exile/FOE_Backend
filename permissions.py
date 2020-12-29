from functools import wraps

from flask import Response
from flask_jwt_extended import get_jwt_identity

from models import User, Guild


def is_active(user):
    if not user.is_active:
        return Response('account is locked', status=403)
    if not user.guild.is_active:
        return Response('guild is locked', status=403)
    if not user.discord_confirmed:
        return Response('has not confirmed account on discord', status=403)


def is_administrator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity()['id'])
        response = is_active(user)
        if response is not None:
            return response
        if user.role not in [User.Role.ADMIN]:
            return Response('requires administrator account', status=403)
        return func(*args, **kwargs)
    return wrapper


def is_verified(func, **kwargs):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity()['id'])
        response = is_active(user)
        if response is not None:
            return response
        if user.role not in [User.Role.VERIFIED, User.Role.ADMIN]:
            return Response('requires verified account', status=403)
        return func(*args, **kwargs)
    return wrapper


def is_discord_bot(func, **kwargs):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity()['id'])
        if not user.username == 'DiscordBot':
            return Response('only discord bot is allowed access', status=403)
        return func(*args, **kwargs)
    return wrapper

def is_guild_leader(func, **kwargs):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity()['id'])
        response = is_active(user)
        if response is not None:
            return response
        if user.role not in [User.Role.GUILD_LEADER, User.Role.ADMIN]:
            return Response('requires Guild leader account', status=403)
        return func(*args, **kwargs)
    return wrapper

def is_alliance_member(func, **kwargs):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity()['id'])
        response = is_active(user)
        if response is not None:
            return response
        if user.role not in [User.Role.ALLIANCE_MEMBER, User.Role.GUILD_LEADER, User.Role.VERIFIED, User.Role.ADMIN]:
            return Response('requires active verified account', status=403)
        guild = Guild.query.first_or_404(id == user.guild)
        if guild.name != 'Flames of Exile':
            return Response('requires a Flames of Exile account', status=403)
        return func(*args, **kwargs)
    return wrapper