import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

socketio = SocketIO()


def create_app(config):
    app = Flask(__name__)
    CORS(app)

    app.config.update(config)

    from models import db
    db.init_app(app)

    from views.campaigns import campaigns
    from views.guilds import guilds
    from views.pins import pins
    from views.users import users
    from views.worlds import worlds
    from views.calendar import calendar
    app.register_blueprint(campaigns)
    app.register_blueprint(guilds)
    app.register_blueprint(pins)
    app.register_blueprint(users)
    app.register_blueprint(worlds)
    app.register_blueprint(calendar)

    JWTManager(app)
    socketio.init_app(app, cors_allowed_origins=os.environ['FRONTEND_URL'])

    return app


if __name__ == '__main__':
    app = create_app()
