import json

from .setup import BasicTests, Method
from models import User


class PermissionsTests(BasicTests):

    def test_jwt_required(self):
        response = self.request('/api/users')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Missing Authorization Header', response.data)

    def test_bogus_jwt(self):
        token = 'Bearer asdf34w234sdf.asdfa34adf.asdfaw34sdf'
        response = self.request('/api/users', headers={'Authorization': token})
        self.assertEqual(response.status_code, 422)

    def test_verified_required_rejects_guest(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id, True).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'discord': 'fakedata', 'token': response.get_json()['token'], 'username': 'new', 'member': False})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        response = self.request('/api/users', headers={'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'requires verified account', response.data)

    def test_verified_required_accepts_verified(self):
        self.register('new', '1qaz!QAZ', self.DEFAULT_GUILD.id, True)
        data = json.dumps({'role': User.Role.VERIFIED.value, 'is_active': True, 'guild_id': self.DEFAULT_GUILD.id})
        self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        token = f'Bearer {self.login("new", "1qaz!QAZ").get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'discord': 'fakedata', 'token': response.get_json()['token'], 'username': 'new', 'member': True})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        response = self.request('/api/users', headers={'Authorization': token})
        self.assertEqual(response.status_code, 200)

    def test_verified_required_accepts_admin(self):
        response = self.request('/api/users', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)

    def test_admin_required_rejects_guest(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id, True).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'discord': 'fakedata', 'token': response.get_json()['token'], 'username': 'new', 'member': True})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        response = self.request('/api/users/1', Method.PUT, {'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'requires Guild leader account', response.data)

    def test_admin_required_rejects_verified(self):
        self.register('new', '1qaz!QAZ', self.DEFAULT_GUILD.id, True)
        data = json.dumps({'role': User.Role.VERIFIED.value, 'is_active': True, 'guild_id': self.DEFAULT_GUILD.id})
        self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        token = f'Bearer {self.login("new", "1qaz!QAZ").get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'discord': 'fakedata', 'token': response.get_json()['token'], 'username': 'new', 'member': True})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        response = self.request('/api/users/1', Method.PUT, {'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'requires Guild leader account', response.data)

    def test_admin_required_accepts_admin(self):
        self.register('new', '1qaz!QAZ', self.DEFAULT_GUILD.id, True)
        data = json.dumps({'role': User.Role.VERIFIED.value, 'is_active': True, 'guild_id': self.DEFAULT_GUILD.id})
        response = self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)

    def test_locked_account(self):
        self.register('new', '1qaz!QAZ', self.DEFAULT_GUILD.id, True)
        data = json.dumps({'role': User.Role.ADMIN.value, 'is_active': False, 'guild_id': self.DEFAULT_GUILD.id})
        self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        token = f'Bearer {self.login("new", "1qaz!QAZ").get_json()["token"]}'
        response = self.request('/api/users', headers={'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'account is locked', response.data)
        response = self.request('/api/users/1', Method.PUT, {'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'account is locked', response.data)

    def test_locked_guild(self):
        self.create_guild(self.DEFAULT_TOKEN, 'new')
        self.register('new', '1qaz!QAZ', self.DEFAULT_GUILD.id, True)
        data = json.dumps({'role': User.Role.ADMIN.value, 'is_active': True, 'guild_id': 2})
        self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        data = json.dumps({'name': 'new', 'is_active': False})
        self.request('/api/guilds/2', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data)
        token = f'Bearer {self.login("new", "1qaz!QAZ").get_json()["token"]}'
        response = self.request('/api/users', headers={'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'guild is locked', response.data)
        response = self.request('/api/users/1', Method.PUT, {'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'guild is locked', response.data)

    def test_unconfirmed_account(self):
        self.register('new', '1qaz!QAZ', self.DEFAULT_GUILD.id, True)
        data = json.dumps({'role': User.Role.ADMIN.value, 'is_active': True, 'guild_id': self.DEFAULT_GUILD.id})
        self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        token = f'Bearer {self.login("new", "1qaz!QAZ").get_json()["token"]}'
        response = self.request('/api/users', headers={'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'has not confirmed account on discord', response.data)
        response = self.request('/api/users/1', Method.PUT, {'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'has not confirmed account on discord', response.data)

    def test_is_discord_bot_allows_bot(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id, True).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'discord': 'fakedata', 'token': response.get_json()['token'], 'username': 'new', 'member': True})
        response = self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)

    def test_is_discord_bot_disallows_others(self):
        self.register('new', '1qaz!QAZ', self.DEFAULT_GUILD.id, True)
        data = json.dumps({'role': User.Role.ADMIN.value, 'is_active': True, 'guild_id': self.DEFAULT_GUILD.id})
        self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        token = f'Bearer {self.login("new", "1qaz!QAZ").get_json()["token"]}'
        response = self.request('/api/users/confirm', Method.PUT, {'Authorization': token}, data)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'only discord bot is allowed access', response.data)
