import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    edits = db.relationship('Edit', backref='user', lazy=True)

    serialize_only = ('id', 'username', 'email', 'edits.id')

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return f'{self.id}: {self.username}'

class Campaign(db.Model, SerializerMixin):
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    image = db.Column(db.String(), nullable=False)
    worlds = db.relationship('World', backref='campaign', lazy=True)

    serialize_only = ('id', 'name', 'image', 'worlds.id')

    def __init__(self, name, image):
        self.name = name
        self.image = image

    def __repr__(self):
        return f'{self.id}: {self.name}'

class World(db.Model, SerializerMixin):
    __tablename__ = 'worlds'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    image = db.Column(db.String(), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)

    serialize_rules = ('-campaign_id',)

    def __init__(self, name, image, campaign_id):
        self.name = name
        self.image = image
        self.campaign_id = campaign_id

    def __repr__(self):
        return f'{self.id}: {self.name}'

class Pin(db.Model, SerializerMixin):
    __tablename__ = "pins"

    id = db.Column(db.Integer, primary_key=True)
    position_x = db.Column(db.Integer, nullable=False)
    position_y = db.Column(db.Integer, nullable=False)
    symbol = db.Column(db.String(), nullable=False)
    world_id = db.Column(db.Integer, db.ForeignKey('worlds.id'), nullable=False)
    edits = db.relationship('Edit', backref='pin', lazy=True)

    serialize_only = ('id', 'position_x', 'position_y', 'symbol', 'world_id', 'edits.id')

    def __init__(self, position_x, position_y, symbol, world_id):
        self.position_x = position_x
        self.position_y = position_y
        self.symbol = symbol
        self.world_id = world_id

    def __repr__(self):
        return f'{self.id}: {self.symbol} - {self.position_x}/{self.position_y}'

class Edit(db.Model, SerializerMixin):
    __tablename__ = "edits"

    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.String())
    date_time = db.Column(db.DateTime(), nullable=False)
    pin_id = db.Column(db.Integer, db.ForeignKey('pins.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    serialize_rules = ('-pin_id', '-user_id')

    def __init__(self, details, pin_id, user_id):
        self.details = details
        self.pin_id = pin_id
        self.user_id = user_id
        self.date_time = datetime.datetime.utcnow()

    def __repr__(self):
        return f'{self.id}: {self.details} - {self.datetime}'