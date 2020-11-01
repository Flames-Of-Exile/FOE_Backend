import json
import unittest

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from passlib.hash import sha256_crypt

from models import db, Campaign, Guild, User
from socketevents import handle_campaign_update, on_connect


class SocketTests(unittest.TestCase):

    def setUp(self):
        app = Flask(__name__)
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = "SUPER-SECRET"
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 300  # 5 minutes
        app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 86400  # 1 day
        app.config['SECURITY_PASSWORD_SALT'] = 'super-secret'

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flamesofexile:flamesofexile@test-db:5432/flamesofexile'

        from views.users import users
        app.register_blueprint(users)

        JWTManager(app)

        with app.app_context():
            db.init_app(app)
            db.drop_all()
            db.create_all()

        self.app = app
        self.test_client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        self.socketio = SocketIO(app)

        self.socketio.on_event('connect', on_connect)
        self.socketio.on_event('campaign-update', handle_campaign_update)

        guild = Guild('Flames of Exile')
        db.session.add(guild)
        db.session.commit()
        foe_guild = db.session.query(Guild).filter_by(name='Flames of Exile').first()

        admin = User('DiscordBot', sha256_crypt.encrypt('admin'), foe_guild.id, User.Role.ADMIN)
        admin.discord_confirmed = True
        db.session.add(admin)
        db.session.commit()

        campaign = Campaign('campaign_name', '/mediafiles/campaign.png', True)
        db.session.add(campaign)
        db.session.commit()

        self.campaign = campaign.to_dict()

        self.maxDiff = None

        self.assertEqual(app.debug, False)

    def tearDown(self):
        self.app_context.pop()

    def test_connection_rejected_without_authentication(self):
        self.test_client.get('/api/users/logout')
        socketio_test_client = self.socketio.test_client(self.app, flask_test_client=self.test_client)
        self.assertFalse(socketio_test_client.is_connected())

    def test_connection_success_with_authentication(self):
        data = json.dumps({'username': 'DiscordBot', 'password': 'admin'})
        self.test_client.post('/api/users/login', data=data, follow_redirects=True, content_type='application/json')
        socketio_test_client = self.socketio.test_client(self.app, flask_test_client=self.test_client)
        self.assertTrue(socketio_test_client.is_connected())

    def test_campaign_update(self):
        data = json.dumps({'username': 'DiscordBot', 'password': 'admin'})
        self.test_client.post('/api/users/login', data=data, follow_redirects=True, content_type='application/json')
        socketio_test_client = self.socketio.test_client(self.app, flask_test_client=self.test_client)
        socketio_test_client.emit('campaign-update')
        data = socketio_test_client.get_received()[0]['args'][0]
        self.assertIn(self.campaign, data)
