import json

from .setup import BasicTests, Method
from models import User


class UserTests(BasicTests):

    def test_list(self):
        response = self.request('/api/users', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertIn(self.DEFAULT_USER.to_dict(), data)

    def test_retrieve(self):
        response = self.request('/api/users/1', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.DEFAULT_USER.to_dict(), response.get_json())

    def test_patch_update_self(self):
        data = json.dumps({'theme': User.Theme.SEABREEZE.value})
        response = self.request('/api/users/1', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"theme":"seabreeze"', response.data)

    def test_patch_update_password(self):
        data = json.dumps({'theme': User.Theme.DEFAULT.value, 'password': '1qaz!QAZ'})
        response = self.request('/api/users/1', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.DEFAULT_USER.to_dict(), response.get_json())
        response = self.login('DiscordBot', '1qaz!QAZ')
        self.assertEqual(response.status_code, 200)

    def test_patch_update_other(self):
        response = self.register('new', '1qaz!QAZ', self.DEFAULT_GUILD.id)
        response = self.request('/api/users/2', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'can only update your own account', response.data)

    def test_put_update_self(self):
        response = self.request('/api/users/1', Method.PUT, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'cannot update your own account', response.data)

    def test_put_update_other(self):
        self.register('new', '1qaz!QAZ', self.DEFAULT_GUILD.id)
        data = json.dumps({'is_active': True, 'role': User.Role.VERIFIED.value,
                           'guild_id': self.DEFAULT_GUILD.id})
        response = self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"is_active":true', response.data)
        self.assertIn(b'"role":"verified"', response.data)

    def test_put_update_password(self):
        self.register('new', '1qaz!QAZ', self.DEFAULT_GUILD.id)
        data = json.dumps({'is_active': True, 'role': User.Role.GUEST.value, 'password': '!QAZ1qaz',
                           'guild_id': self.DEFAULT_GUILD.id})
        response = self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)
        response = self.login('new', '!QAZ1qaz')
        self.assertEqual(response.status_code, 200)

    def test_confirm_discord_success(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': response.get_json()['token'], 'username': 'new', 'discord': 'dummyvalue', 'member': True})
        response = self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"discord_confirmed":true', response.data)

    def test_confirm_discord_fail_already_confirmed(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': response.get_json()['token'], 'username': 'new', 'discord': 'dummyvalue', 'member': True})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        response = self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'user has already confirmed their discord', response.data)

    def test_confirm_discord_fail_invalid_token(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': 'badvalue', 'username': 'new', 'discord': 'dummyvalue'})
        response = self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'invalid user/token', response.data)

    def test_confirm_discord_fail_username_not_found(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': response.get_json()['token'], 'username': 'badusername', 'discord': 'dummyvalue'})
        response = self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 404)

    def test_confirm_discord_fail_unique_id(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': response.get_json()['token'], 'username': 'new', 'discord': 'dummyvalue', 'member': True})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        token = f'Bearer {self.register("new2", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': response.get_json()['token'],
                           'username': 'new2', 'discord': 'dummyvalue', 'member': False})
        response = self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Key (discord)=(dummyvalue) already exists.', response.data)

    def test_discord_set_member_status_verified(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': response.get_json()['token'], 'username': 'new', 'discord': 'dummyvalue', 'member': True})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        response = self.request('/api/users/2', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.get_json()['role'], 'verified')

    def test_discord_set_member_status_guest(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': response.get_json()['token'], 'username': 'new', 'discord': 'dummyvalue', 'member': False})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        response = self.request('/api/users/2', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.get_json()['role'], 'guest')

    def test_discord_revoke_member(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': response.get_json()['token'], 'username': 'new', 'discord': 'dummyvalue', 'member': True})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        data = json.dumps({'token': response.get_json()['token'], 'discord': 'dummyvalue', 'is_active': False, 'role': 'guest'})
        self.request('/api/users/discordroles/dummyvalue', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data)
        response = self.request('/api/users/2', headers={'Authorization': self.DEFAULT_TOKEN})
        print(response.get_json())
        self.assertEqual(response.get_json()['role'], 'guest')
        self.assertEqual(response.get_json()['is_active'], False)

    def test_discord_grant_member(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': response.get_json()['token'], 'username': 'new', 'discord': 'dummyvalue', 'member': True})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        data = json.dumps({'token': response.get_json()['token'], 'discord': 'dummyvalue', 'is_active': True, 'role': 'admin'})
        self.request('/api/users/discordroles/dummyvalue', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data)
        response = self.request('/api/users/2', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.get_json()['role'], 'admin')
        self.assertEqual(response.get_json()['is_active'], True)

    def test_send_discord_token_success(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.get_json().keys())

    def test_send_discord_token_fail(self):
        response = self.request('/api/users/discord-token', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'user has already confirmed their discord', response.data)

    def test_discord_whoami(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': response.get_json()['token'], 'username': 'new', 'discord': 'test', 'member': True})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        response = self.request('/api/users/discord/test', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset({'username': 'new', 'discord_confirmed': True}, response.get_json())

    def test_discord_password_reset_success(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': response.get_json()['token'], 'username': 'new', 'discord': 'test', 'member': True})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        data = json.dumps({'password': '!QAZ1qaz'})
        response = self.request('/api/users/password-reset/test', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)
        response = self.login('new', '!QAZ1qaz')
        self.assertEqual(response.status_code, 200)

    def test_discord_password_reset_fail(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", self.DEFAULT_GUILD.id).get_json()["token"]}'
        response = self.request('/api/users/discord-token', headers={'Authorization': token})
        data = json.dumps({'token': response.get_json()['token'], 'username': 'new', 'discord': 'test', 'member': True})
        self.request('/api/users/confirm', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        data = json.dumps({'password': 'badpass'})
        response = self.request('/api/users/password-reset/test', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 400)
        response = self.login('new', 'badpass')
        self.assertEqual(response.status_code, 400)
