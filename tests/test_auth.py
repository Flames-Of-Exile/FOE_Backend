from .setup import BasicTests
from models import User

from passlib.hash import sha256_crypt


class AuthTests(BasicTests):

    def test_login_success(self):
        response = self.login('DiscordBot', 'admin')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn('token', data)
        self.assertEqual(self.DEFAULT_USER.to_dict(), data['user'])
        self.assertIn('Set-Cookie', response.headers)

    def test_login_fails(self):
        response = self.login('DiscordBot', 'wrongpassword')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'invalid username/password', response.data)
        self.assertNotIn('Set-Cookie', response.headers)

        response = self.login('wrongusername', 'admin')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'invalid username/password', response.data)
        self.assertNotIn('Set-Cookie', response.headers)

        response = self.login('', '')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'invalid username/password', response.data)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_register_success(self):
        user = User('new', sha256_crypt.encrypt('1qaz!QAZ'), self.DEFAULT_GUILD.id, User.Role.GUEST)
        user.id = 2

        response = self.register('new', '1qaz!QAZ', self.DEFAULT_GUILD.id)
        self.assertEqual(response.status_code, 201)
        user.guild = self.DEFAULT_GUILD

        data = response.get_json()
        self.assertIn('token', data)
        self.assertEqual(user.to_dict(), data['user'])
        self.assertIn('Set-Cookie', response.headers)

    def test_register_fail_unique_username(self):
        response = self.register('DiscordBot', '1qaz!QAZ', self.DEFAULT_GUILD.id)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Key (username)=(DiscordBot) already exists.', response.data)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_register_fail_empty_username(self):
        response = self.register('', '1qaz!QAZ', self.DEFAULT_GUILD.id)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'null value in column "username" violates not-null constraint', response.data)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_register_fail_empty_password(self):
        response = self.register('new', '', self.DEFAULT_GUILD.id)
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_logout(self):
        response = self.logout()
        self.assertIn('refresh_token=;', response.headers['Set-Cookie'])

    def test_password_complexity_length_fail(self):
        response = self.register('new', '1qaz!QA', self.DEFAULT_GUILD.id)
        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        marked_errors = list(filter(lambda key: data[key] is True, data.keys()))
        self.assertEqual(len(marked_errors), 1)
        self.assertIn('length_error', marked_errors)

    def test_password_complexity_digit_fail(self):
        response = self.register('new', 'qqaz!QAZ', self.DEFAULT_GUILD.id)
        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        marked_errors = list(filter(lambda key: data[key] is True, data.keys()))
        self.assertEqual(len(marked_errors), 1)
        self.assertIn('digit_error', marked_errors)

    def test_password_complexity_lowercase_fail(self):
        response = self.register('new', '1QAZ!QAZ', self.DEFAULT_GUILD.id)
        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        marked_errors = list(filter(lambda key: data[key] is True, data.keys()))
        self.assertEqual(len(marked_errors), 1)
        self.assertIn('lowercase_error', marked_errors)

    def test_password_complexity_uppercase_fail(self):
        response = self.register('new', '1qaz!qaz', self.DEFAULT_GUILD.id)
        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        marked_errors = list(filter(lambda key: data[key] is True, data.keys()))
        self.assertEqual(len(marked_errors), 1)
        self.assertIn('uppercase_error', marked_errors)

    def test_password_complexity_symbol_fail(self):
        response = self.register('new', '1qaz1QAZ', self.DEFAULT_GUILD.id)
        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        marked_errors = list(filter(lambda key: data[key] is True, data.keys()))
        self.assertEqual(len(marked_errors), 1)
        self.assertIn('symbol_error', marked_errors)

    def test_password_complexity_multi_fail(self):
        response = self.register('new', '1qaz', self.DEFAULT_GUILD.id)
        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        marked_errors = list(filter(lambda key: data[key] is True, data.keys()))
        self.assertEqual(len(marked_errors), 3)
        self.assertIn('length_error', marked_errors)
        self.assertIn('uppercase_error', marked_errors)
        self.assertIn('symbol_error', marked_errors)

    def test_refresh_success(self):
        response = self.request('/api/users/refresh')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn('token', data)
        self.assertEqual(self.DEFAULT_USER.to_dict(), data['user'])

    def test_refresh_no_cookie_fail(self):
        self.logout()
        response = self.request('/api/users/refresh')
        self.assertEqual(response.status_code, 422)
        self.assertIn(b'Invalid token type.', response.data)
