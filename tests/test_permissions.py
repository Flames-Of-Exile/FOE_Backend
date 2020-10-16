import json

from .setup import BasicTests, Method


class PermissionsTests(BasicTests):

    def test_jwt_required(self):
        response = self.request('/api/users')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Missing Authorization Header', response.data)

    def test_bogus_jwt(self):
        token = 'Bearer asdf34w234sdf.asdfa34adf.asdfaw34sdf'
        response = self.request('/api/users', Method.GET, {'Authorization': token})
        self.assertEqual(response.status_code, 422)

    def test_member_required_rejects_guest(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", "new@email.com").get_json()["token"]}'
        response = self.request('/api/users', Method.GET, {'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'requires member account', response.data)

    def test_member_required_accepts_member(self):
        self.register('new', '1qaz!QAZ', 'new@email.com')
        data = json.dumps({'role': 'member', 'is_active': True, 'email': 'new@email.com', })
        self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        token = f'Bearer {self.login("new", "1qaz!QAZ").get_json()["token"]}'
        response = self.request('/api/users', Method.GET, {'Authorization': token})
        self.assertEqual(response.status_code, 200)

    def test_member_required_accepts_admin(self):
        response = self.request('/api/users', Method.GET, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)

    def test_admin_required_rejects_guest(self):
        token = f'Bearer {self.register("new", "1qaz!QAZ", "new@email.com").get_json()["token"]}'
        response = self.request('/api/users/1', Method.PUT, {'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'requires administrator account', response.data)

    def test_admin_required_rejects_member(self):
        self.register('new', '1qaz!QAZ', 'new@email.com')
        data = json.dumps({'role': 'member', 'is_active': True, 'email': 'new@email.com', })
        self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        token = f'Bearer {self.login("new", "1qaz!QAZ").get_json()["token"]}'
        response = self.request('/api/users/1', Method.PUT, {'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'requires administrator account', response.data)

    def test_admin_required_accepts_admin(self):
        self.register('new', '1qaz!QAZ', 'new@email.com')
        data = json.dumps({'role': 'member', 'is_active': True, 'email': 'new@email.com', })
        response = self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)

    def test_locked_account(self):
        self.register('new', '1qaz!QAZ', 'new@email.com')
        data = json.dumps({'role': 'admin', 'is_active': False, 'email': 'new@email.com', })
        self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        token = f'Bearer {self.login("new", "1qaz!QAZ").get_json()["token"]}'
        response = self.request('/api/users', Method.GET, {'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'account is locked', response.data)
        response = self.request('/api/users/1', Method.PUT, {'Authorization': token})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'account is locked', response.data)
