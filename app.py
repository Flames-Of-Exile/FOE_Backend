import os

from flask import Flask
from flask_mail import Mail
from flask_jwt_extended import JWTManager


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 300  # 5 minutes
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 86400  # 1 day

    app.config['SECURITY_PASSWORD_SALT'] = os.environ['SECURITY_PASSWORD_SALT']

    from models import db
    db.init_app(app)

    from views.campaigns import campaigns
    from views.pins import pins
    from views.users import users
    from views.worlds import worlds
    app.register_blueprint(campaigns)
    app.register_blueprint(pins)
    app.register_blueprint(users)
    app.register_blueprint(worlds)

    JWTManager(app)
    Mail(app)

    return app


if __name__ == '__main__':
    app = create_app()
