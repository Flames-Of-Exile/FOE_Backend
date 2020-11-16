import datetime
import enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    class Role(enum.Enum):
        GUEST = 'guest'
        VERIFIED = 'verified'
        ADMIN = 'admin'

    class Theme(enum.Enum):
        DEFAULT = 'default'
        BLUE_RASPBERRY = 'blue_raspberry'
        SEABREEZE = 'seabreeze'
        CARTOGRAPHY = 'cartography'
        PUMPKIN_SPICE = 'pumpkin_spice'
        RED = 'red'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    discord = db.Column(db.String(), unique=True)
    is_active = db.Column(db.Boolean(), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)
    theme = db.Column(db.Enum(Theme), nullable=False)
    discord_confirmed = db.Column(db.Boolean(), nullable=False)
    edits = db.relationship('Edit', backref='user', lazy=True)
    guild_id = db.Column(db.Integer, db.ForeignKey('guilds.id'), nullable=False)

    serialize_only = ('id', 'username', 'is_active', 'role', 'theme', 'edits.id', 'discord_confirmed',
                      'guild.id', 'guild.name', 'guild.is_active')

    def __init__(self, username, password, guild_id, role=Role.GUEST):
        self.username = username
        self.password = password
        self.discord = None
        self.is_active = True
        self.role = role
        self.theme = User.Theme.DEFAULT
        self.discord_confirmed = False
        self.guild_id = guild_id

    def __repr__(self):
        return f'{self.id}: {self.username}'


class Campaign(db.Model, SerializerMixin):
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    image = db.Column(db.String(), nullable=False, unique=True)
    worlds = db.relationship('World', backref='campaign', lazy=True)
    is_default = db.Column(db.Boolean())
    is_archived = db.Column(db.Boolean())

    serialize_rules = ('-worlds.campaign',)

    def __init__(self, name, image, is_default=False):
        self.name = name
        self.image = image
        self.is_default = is_default
        self.is_archived = False

    def __repr__(self):
        return f'{self.id}: {self.name}'


class World(db.Model, SerializerMixin):
    __tablename__ = 'worlds'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    image = db.Column(db.String(), nullable=False, unique=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    pins = db.relationship('Pin', backref='world', lazy=True)

    serialize_rules = ('-campaign_id', '-pins.world')

    def __init__(self, name, image, campaign_id):
        self.name = name
        self.image = image
        self.campaign_id = campaign_id

    def __repr__(self):
        return f'{self.id}: {self.name}'


class Pin(db.Model, SerializerMixin):
    __tablename__ = "pins"

    class Symbol(enum.Enum):
        STONE = 'stone'
        STONE_MOTHERLODE = 'stone-motherlode'
        ORE = 'ore'
        ORE_MOTHERLODE = 'ore-motherlode'
        WOOD = 'wood'
        ANIMAL = 'animal'
        ANIMAL_BOSS = 'animal-boss'
        MOB = 'mob'
        MOB_BOSS = 'mob-boss'
        WELL = 'well'
        GRAVE = 'grave'
        TACTICAL_HOUSE = 'tactical-house'
        TACTICAL_FIRE = 'tactical-fire'
        TACTICAL_FISH = 'tactical-fish'

    class Resource(enum.Enum):
        YEW = 'yew'
        BIRCH = 'birch'
        ASH = 'ash'
        OAK = 'oak'
        SPRUCE = 'spruce'
        COPPER = 'copper'
        TIN = 'tin'
        IRON = 'iron'
        SILVER = 'silver'
        AURELIUM = 'aurelium'
        GRANITE = 'granite'
        LIMESTONE = 'limestone'
        TRAVERTINE = 'travertine'
        SLATE = 'slate'
        MARBLE = 'marble'
        SPIDER = 'spider'
        PIG = 'pig'
        CAT = 'cat'
        AUROCH = 'auroch'
        ELK = 'elk'
        WOLF = 'wolf'
        HUMAN = 'human'
        ELVEN = 'elven'
        MONSTER = 'monster'
        STONEBORN = 'stoneborn'
        GUINECIAN = 'guinecian'
        NA = 'na'

    id = db.Column(db.Integer, primary_key=True)
    position_x = db.Column(db.Float, nullable=False)
    position_y = db.Column(db.Float, nullable=False)
    symbol = db.Column(db.Enum(Symbol), nullable=False)
    resource = db.Column(db.Enum(Resource), nullable=False)
    rank = db.Column(db.Integer)
    name = db.Column(db.String())
    amount = db.Column(db.Integer)
    notes = db.Column(db.String())
    respawn = db.Column(db.Integer)
    world_id = db.Column(db.Integer, db.ForeignKey('worlds.id'), nullable=False)
    edits = db.relationship('Edit', backref='pin', lazy=True, cascade='all, delete')
    x_cord = db.Column(db.String(1))
    y_cord = db.Column(db.Float)

    serialize_rules = ('-edits.pin',)

    def __init__(self, position_x, position_y, symbol, resource,
                 world_id, rank, name, amount, respawn, notes,
                 x_cord, y_cord):
        self.position_x = position_x
        self.position_y = position_y
        self.symbol = symbol
        self.resource = resource
        self.world_id = world_id
        self.rank = rank
        self.name = name
        self.amount = amount
        self.respawn = respawn
        self.notes = notes
        self.x_cord = x_cord
        self.y_cord = y_cord

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


class Guild(db.Model, SerializerMixin):
    __tablename__ = "guilds"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    is_active = db.Column(db.Boolean(), nullable=False)
    users = db.relationship('User', backref='guild', lazy=True)

    serialize_rules = ('-users.guild', '-users.email')

    def __init__(self, name):
        self.name = name
        self.is_active = True

    def __repr__(self):
        return f'{self.id}: {self.name} - {self.is_active}'
