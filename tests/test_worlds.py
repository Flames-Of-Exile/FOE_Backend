from .setup import BasicTests, Method

from models import World


class WorldTests(BasicTests):

    def test_list(self):
        response = self.request('/api/worlds', Method.GET, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertIn(self.DEFAULT_WORLD.to_dict(), data)

    def test_retrieve(self):
        response = self.request('/api/worlds/1', Method.GET, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.DEFAULT_WORLD.to_dict(), response.get_json())

    def test_create_success(self):
        world = World('new', '/mediafiles/file.jpg', 1)
        world.id = 2
        world = world.to_dict()
        del world['campaign']

        response = self.create_world(self.DEFAULT_TOKEN, 'new', 'file.jpg', 1)

        self.assertEqual(response.status_code, 201)
        json = response.get_json()
        del json['campaign']
        self.assertEqual(world, json)

    def test_create_fail_unique_filename(self):
        pass

    def test_create_fail_invalid_extension(self):
        pass

    def test_create_fail_invalid_campaign(self):
        pass

    def test_update(self):
        pass
