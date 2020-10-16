from .setup import BasicTests, Method

from models import Campaign


class CampaignTests(BasicTests):

    def test_list(self):
        response = self.request('/api/campaigns', Method.GET, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertIn(self.DEFAULT_CAMPAIGN.to_dict(), data)

    def test_retrieve(self):
        response = self.request('/api/campaigns/1', Method.GET, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.DEFAULT_CAMPAIGN.to_dict(), response.get_json())

    def test_query_name_found(self):
        response = self.request('/api/campaigns/q?name=campaign_name', Method.GET, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.DEFAULT_CAMPAIGN.to_dict(), response.get_json())

    def test_query_name_not_found(self):
        response = self.request('/api/campaigns/q?name=bad_name', Method.GET, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 404)

    def test_create_success(self):
        campaign = Campaign('new', '/mediafiles/file.jpg')
        campaign.id = 2

        token = f'Bearer {self.login("admin", "admin").get_json()["token"]}'
        response = self.create_campaign(token, 'new', 'file.jpg', False)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(campaign.to_dict(), response.get_json())

    def test_create_fail_unique_name(self):
        pass

    def test_create_fail_unique_filename(self):
        pass

    def test_create_fail_invalid_extension(self):
        pass

    def test_update(self):
        pass

    def test_list_archived(self):
        pass

    def test_list_no_archived(self):
        pass

    def test_list_default_first(self):
        pass
