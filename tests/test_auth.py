from .setup import BasicTests
from models import User


class AuthTests(BasicTests):

    def test_login_success(self):
        user = User('admin', '21232f297a57a5a743894a0e4a801fc3', 'email@email.com', User.Role.ADMIN)
        user.id = 1

        response = self.login('admin', 'admin')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn('token', data)
        self.assertEqual(user.to_dict(), data['user'])
        self.assertIn('Set-Cookie', response.headers)

    def test_login_fails(self):
        response = self.login('admin', 'wrongpassword')
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
        user = User('new', '21232f297a57a5a743894a0e4a801fc3', 'new@email.com', User.Role.GUEST)
        user.id = 2

        response = self.register('new', 'admin', 'new@email.com')
        self.assertEqual(response.status_code, 201)

        data = response.get_json()
        self.assertIn('token', data)
        self.assertEqual(user.to_dict(), data['user'])
        self.assertIn('Set-Cookie', response.headers)

    def test_register_fail_unique_username(self):
        response = self.register('admin', 'admin', 'new@email.com')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Key (username)=(admin) already exists.', response.data)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_register_fail_unique_email(self):
        response = self.register('new', 'admin', 'email@email.com')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Key (email)=(email@email.com) already exists.', response.data)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_register_fail_empty_username(self):
        response = self.register('', 'admin', 'new@email.com')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'null value in column "username" violates not-null constraint', response.data)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_register_fail_empty_password(self):
        response = self.register('new', '', 'new@email.com')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'null value in column "password" violates not-null constraint', response.data)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_register_fail_empty_email(self):
        response = self.register('new', 'admin', '')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'null value in column "email" violates not-null constraint', response.data)
        self.assertNotIn('Set-Cookie', response.headers)

    def test_logout(self):
        response = self.app.get('/api/users/logout', follow_redirects=True)
        self.assertIn('refresh_token=;', response.headers['Set-Cookie'])