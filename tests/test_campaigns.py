import json

from .setup import BasicTests, Method
from models import Campaign


class CampaignTests(BasicTests):

    def test_list(self):
        response = self.request('/api/campaigns', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertIn(self.DEFAULT_CAMPAIGN.to_dict(), data)

    def test_retrieve(self):
        response = self.request('/api/campaigns/1', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.DEFAULT_CAMPAIGN.to_dict(), response.get_json())

    def test_query_name_found(self):
        response = self.request('/api/campaigns/q?name=campaign_name', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.DEFAULT_CAMPAIGN.to_dict(), response.get_json())

    def test_query_name_not_found(self):
        response = self.request('/api/campaigns/q?name=bad_name', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 404)

    def test_create_success(self):
        campaign = Campaign('new', '/mediafiles/file.jpg')
        campaign.id = 2
        response = self.create_campaign(self.DEFAULT_TOKEN, 'new', 'file.jpg', 'false')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(campaign.to_dict(), response.get_json())

    def test_create_fail_unique_name(self):
        response = self.create_campaign(self.DEFAULT_TOKEN, 'campaign_name', 'file.jpg', 'false')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'duplicate key value violates unique constraint "campaigns_name_key"', response.data)

    def test_create_fail_unique_filename(self):
        response = self.create_campaign(self.DEFAULT_TOKEN, 'new', 'campaign.png', 'false')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'duplicate key value violates unique constraint "campaigns_image_key"', response.data)

    def test_create_fail_invalid_extension(self):
        response = self.create_campaign(self.DEFAULT_TOKEN, 'new', 'file.pdf', 'false')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'invalid file type', response.data)

    def test_update(self):
        data = json.dumps({
            'is_default': True,
            'is_archived': False,
            'name': 'updated_name'
        })
        response = self.request('/api/campaigns/1', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data)
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset({'is_default': True, 'is_archived': False,
                                       'name': 'updated_name', 'image': '/mediafiles/campaign.png'},
                                      response.get_json())

    def test_list_archived(self):
        data = json.dumps({
            'is_default': False,
            'is_archived': True,
            'name': 'campaign_name'
        })
        self.request('/api/campaigns/1', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data)
        response = self.request('/api/campaigns/archived', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertDictContainsSubset({'is_default': False, 'is_archived': True,
                                       'name': 'campaign_name', 'image': '/mediafiles/campaign.png'},
                                      data[0])

    def test_list_no_archived(self):
        data = json.dumps({
            'is_default': False,
            'is_archived': True,
            'name': 'campaign_name'
        })
        self.request('/api/campaigns/1', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, data)
        response = self.request('/api/campaigns', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 0)

    def test_list_default_first(self):
        self.create_campaign(self.DEFAULT_TOKEN, 'default_campaign', 'default_campaign.jpg', 'true')
        self.create_campaign(self.DEFAULT_TOKEN, 'newest_campaign', 'newest_campaign.jpg', 'false')
        response = self.request('/api/campaigns', headers={'Authorization': self.DEFAULT_TOKEN})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['name'], 'default_campaign')
        self.assertEqual(data[1]['name'], 'newest_campaign')
