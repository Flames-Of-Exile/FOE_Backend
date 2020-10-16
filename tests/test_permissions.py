from .setup import BasicTests
from models import User


class PermissionsTests(BasicTests):

    def test_jwt_required(self):
        response = self.app.get('/api/users', follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Missing Authorization Header', response.data)
