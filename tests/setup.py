import json
import unittest

from flask import Flask
from flask_jwt_extended import JWTManager

from models import db, User


class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app = Flask(__name__)
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = "SUPER-SECRET"
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 300  # 5 minutes
        app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 86400  # 1 day

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flamesofexile:flamesofexile@test-db:5432/flamesofexile'

        from views.campaigns import campaigns
        from views.pins import pins
        from views.users import users
        from views.worlds import worlds
        app.register_blueprint(campaigns)
        app.register_blueprint(pins)
        app.register_blueprint(users)
        app.register_blueprint(worlds)

        JWTManager(app)

        with app.app_context():
            db.init_app(app)
            db.drop_all()
            db.create_all()

        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        admin = User('admin', '21232f297a57a5a743894a0e4a801fc3', 'email@email.com', User.Role.ADMIN)
        db.session.add(admin)
        db.session.commit()

        self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
        self.app_context.pop()

    def login(self, username, password):
        data = json.dumps({'username': username, 'password': password})
        return self.app.post('/api/users/login', data=data, follow_redirects=True, content_type='application/json')

    def register(self, username, password, email):
        data = json.dumps({'username': username, 'password': password, 'email': email})
        return self.app.post('/api/users', data=data, follow_redirects=True, content_type='application/json')
