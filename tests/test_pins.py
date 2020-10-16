import json

from .setup import BasicTests, Method

from models import Pin


class PinTests(BasicTests):

    def test_list(self):
        response = self.request('/api/pins', Method.GET, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertIn(self.DEFAULT_PIN.to_dict(), data)

    def test_retrieve(self):
        response = self.request('/api/pins/1', Method.GET, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.DEFAULT_PIN.to_dict(), response.get_json())

    def test_create_success(self):
        pass

    def test_create_fail(self):
        pass

    def test_update(self):
        pass

    def test_delete(self):
        pass
