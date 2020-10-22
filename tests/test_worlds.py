import io

from .setup import BasicTests, Method
from models import World


class WorldTests(BasicTests):

    def test_list(self):
        response = self.request('/api/worlds', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertIn(self.DEFAULT_WORLD.to_dict(), data)

    def test_retrieve(self):
        response = self.request('/api/worlds/1', headers={'Authorization': self.DEFAULT_TOKEN})
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
        self.assertDictContainsSubset(world, json)

    def test_create_fail_unique_filename(self):
        response = self.create_world(self.DEFAULT_TOKEN, 'new', 'world.png', 1)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'duplicate key value violates unique constraint "worlds_image_key"', response.data)

    def test_create_fail_invalid_extension(self):
        response = self.create_world(self.DEFAULT_TOKEN, 'new', 'file.pdf', 1)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'invalid file type', response.data)

    def test_create_fail_invalid_campaign(self):
        response = self.create_world(self.DEFAULT_TOKEN, 'new', 'file.jpg', 2)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'violates foreign key constraint "worlds_campaign_id_fkey"', response.data)

    def test_update(self):
        data = {
            'file': ((io.BytesIO(b'mockdata')), 'updatedname.png'),
            'name': 'updated_name',
            'campaign_id': 1
        }
        response = self.request('/api/worlds/1', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data,
                                'multipart/form-data')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertDictContainsSubset({'image': '/mediafiles/updatedname.png', 'name': 'updated_name'}, data)
