import enum
import io
import json
import unittest
import datetime

from passlib.hash import sha256_crypt

from app import create_app
from config import test_config
from models import db, Campaign, Edit, Guild, Pin, User, World, Event


class Method(enum.Enum):
    DELETE = 'delete'
    GET = 'get'
    PATCH = 'patch'
    POST = 'post'
    PUT = 'put'


class BasicTests(unittest.TestCase):

    def setUp(self):
        app = create_app(test_config)

        with app.app_context():
            db.drop_all()
            db.create_all()

        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        guild = Guild('Flames of Exile')
        db.session.add(guild)
        db.session.commit()
        foe_guild = db.session.query(Guild).filter_by(name='Flames of Exile').first()

        admin = User('DiscordBot', sha256_crypt.encrypt('admin'), foe_guild.id, User.Role.ADMIN)
        admin.discord_confirmed = True
        db.session.add(admin)
        db.session.commit()

        campaign = Campaign('campaign_name', '/mediafiles/campaigns/campaign.png', True)
        db.session.add(campaign)
        db.session.commit()

        world = World('world_name', '/mediafiles/campaigns/campaign_name/world.png', 1, 1, 1, 1)
        db.session.add(world)
        db.session.commit()

        pin = Pin(1, 1, Pin.Symbol.ANIMAL, Pin.Resource.WOLF, 1, 1, '', 1, 1, 'notes', 1, 1)
        db.session.add(pin)
        db.session.commit()

        edit = Edit("", 1, 1)
        db.session.add(edit)
        db.session.commit()

        event = Event('event', 'game', datetime.datetime.now().isoformat(), 'note')
        db.session.add(event)
        db.session.commit()

        self.DEFAULT_GUILD = guild
        self.DEFAULT_USER = admin
        self.DEFAULT_CAMPAIGN = campaign
        self.DEFAULT_WORLD = world
        self.DEFAULT_PIN = pin
        self.DEFAULT_TOKEN = f'Bearer {self.login("DiscordBot", "admin").get_json()["token"]}'
        self.DEFAULT_EVENT = event

        self.maxDiff = None

        self.assertEqual(app.debug, False)

    def tearDown(self):
        self.app_context.pop()

    def request(self, url, method=Method.GET, headers={}, data={}, content_type='application/json'):
        if method is Method.DELETE:
            return self.app.delete(url, follow_redirects=True, headers=headers)
        if method is Method.GET:
            return self.app.get(url, follow_redirects=True, headers=headers)
        if method is Method.PATCH:
            return self.app.patch(url, data=data, follow_redirects=True, content_type=content_type, headers=headers)
        if method is Method.PUT:
            return self.app.put(url, data=data, follow_redirects=True, content_type=content_type, headers=headers)
        if method is Method.POST:
            return self.app.post(url, data=data, follow_redirects=True, content_type=content_type, headers=headers)

    def login(self, username, password):
        data = json.dumps({'username': username, 'password': password})
        return self.request('/api/users/login', Method.POST, {}, data)

    def register(self, username, password, guild_id, currentMember):
        data = json.dumps({'username': username, 'password': password, 'guild_id': guild_id, 'currentMember': currentMember})
        return self.request('/api/users', Method.POST, {}, data)

    def logout(self):
        return self.request('/api/users/logout')

    def create_campaign(self, token, name, filename, is_default):
        data = {'name': name, 'is_default': is_default, 'file': (io.BytesIO(b'mockdata'), filename)}
        headers = {'Authorization': token}
        return self.request('/api/campaigns', Method.POST, headers, data, 'multipart/form-data')

    def create_world(self, token, name, filename, center_lng, center_lat, radius, campaign_id):
        data = {'name': name, 'campaign_id': campaign_id, 'file': (io.BytesIO(b'mockdata'), filename),
                'center_lng': center_lng, 'center_lat': center_lat, 'radius': radius}
        headers = {'Authorization': token}
        return self.request('/api/worlds', Method.POST, headers, data, 'multipart/form-data')

    def create_pin(self, token, position_x, position_y, symbol,
                   resource, world_id, rank=0, name='',
                   amount=0, respawn=0, notes='', x_cord=1, y_cord=1):
        data = json.dumps({
            'position_x': position_x,
            'position_y': position_y,
            'symbol': symbol,
            'resource': resource,
            'world_id': world_id,
            'rank': rank,
            'name': name,
            'amount': amount,
            'respawn': respawn,
            'notes': notes,
            'x_cord': x_cord,
            'y_cord': y_cord
        })
        headers = {'Authorization': token}
        return self.request('/api/pins', Method.POST, headers, data)

    def create_guild(self, token, name):
        data = json.dumps({'name': name})
        headers = {'Authorization': token}
        return self.request('/api/guilds', Method.POST, headers, data)

    def create_event(self, name, game, date, note, token):
        data = json.dumps({
            'name': name,
            'game': game,
            'date': date,
            'note': note
        })
        headers = {'Authorization': token}
        return self.request('/api/calendar', Method.POST, headers, data)

    def edit_event(self, id, name, game, date, note, token):
        data = json.dumps({
            'name': name,
            'game': game,
            'date': date,
            'note': note
        })
        headers = {'Authorization': token}
        return self.request(f'/api/calendar/{id}', Method.PATCH, headers, data)