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
        data = json.dumps({'email': 'updated@email.com', 'theme': User.Theme.SEABREEZE.value})
        response = self.request('/api/users/1', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"theme":"seabreeze"', response.data)
        self.assertIn(b'"email":"updated@email.com"', response.data)

    def test_patch_update_password(self):
        data = json.dumps({'email': 'email@email.com', 'theme': User.Theme.DEFAULT.value, 'password': '1qaz!QAZ'})
        response = self.request('/api/users/1', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.DEFAULT_USER.to_dict(), response.get_json())
        response = self.login('admin', '1qaz!QAZ')
        self.assertEqual(response.status_code, 200)

    def test_patch_update_other(self):
        response = self.register('new', '1qaz!QAZ', 'new@email.com')
        response = self.request('/api/users/2', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'can only update your own account', response.data)

    def test_put_update_self(self):
        response = self.request('/api/users/1', Method.PUT, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'cannot update your own account', response.data)

    def test_put_update_other(self):
        response = self.register('new', '1qaz!QAZ', 'new@email.com')
        data = json.dumps({'email': 'updated@email.com', 'is_active': True, 'role': User.Role.MEMBER.value})
        response = self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"is_active":true', response.data)
        self.assertIn(b'"email":"updated@email.com"', response.data)
        self.assertIn(b'"role":"member"', response.data)

    def test_put_update_password(self):
        response = self.register('new', '1qaz!QAZ', 'new@email.com')
        data = json.dumps({'email': 'new@email.com', 'is_active': True, 'role': User.Role.GUEST.value, 'password': '!QAZ1qaz'})
        response = self.request('/api/users/2', Method.PUT, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)
        response = self.login('new', '!QAZ1qaz')
        self.assertEqual(response.status_code, 200)
