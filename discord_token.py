from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadTimeSignature


def generate_confirmation_token(username):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(username, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        username = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except BadTimeSignature:
        return False
    return username
