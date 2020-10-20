import json

from .setup import BasicTests, Method

from models import Guild


class GuildTests(BasicTests):

    def test_list(self):
        response = self.request('/api/guilds')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertIn(self.DEFAULT_GUILD.to_dict(), data)

    def test_retrieve(self):
        response = self.request('/api/guilds/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.DEFAULT_GUILD.to_dict(), response.get_json())

    def test_query_name_found(self):
        response = self.request('/api/guilds/q?name=Flames of Exile')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.DEFAULT_GUILD.to_dict(), response.get_json())

    def test_query_name_not_found(self):
        response = self.request('/api/guilds/q?name=bad_name')
        self.assertEqual(response.status_code, 404)

    def test_create_success(self):
        guild = Guild('new')
        guild.id = 2
        response = self.create_guild(self.DEFAULT_TOKEN, 'new')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(guild.to_dict(), response.get_json())

    def test_create_fail_unique_name(self):
        response = self.create_guild(self.DEFAULT_TOKEN, 'Flames of Exile')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'duplicate key value violates unique constraint "guilds_name_key"', response.data)

    def test_update_success(self):
        self.create_guild(self.DEFAULT_TOKEN, 'new')
        data = {'name': 'updated name', 'is_active': False}
        response = self.request('/api/guilds/2', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, json.dumps(data))
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset(data, response.get_json())

    def test_update_fail_main_guild(self):
        response = self.request('/api/guilds/1', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'no editing the main guild', response.data)
