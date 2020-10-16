import json

from .setup import BasicTests
from models import User


class UserTests(BasicTests):

    def test_list(self):
        user1 = User('admin', '21232f297a57a5a743894a0e4a801fc3', 'email@email.com', User.Role.ADMIN)
        user1.id = 1
        user2 = User('new', '21232f297a57a5a743894a0e4a801fc3', 'new@email.com', User.Role.GUEST)
        user2.id = 2
        self.register('new', 'admin', 'new@email.com')

        token = f'Bearer {json.loads(self.login("admin", "admin").get_data(as_text=True))["token"]}'
        response = self.app.get('/api/users', follow_redirects=True, headers={'Authorization': token})
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertIn(user1.to_dict(), data)
        self.assertIn(user2.to_dict(), data)
