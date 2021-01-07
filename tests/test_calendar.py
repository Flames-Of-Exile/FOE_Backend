import json
from json import JSONEncoder
from datetime import datetime
from .setup import BasicTests, Method
from models import Event

class CalendarTests(BasicTests):

    def test_get_all_events(self):
        response = self.request('/api/calendar', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertIn(self.DEFAULT_EVENT.to_dict(), data)

    def test_delete_event(self):
        response = self.request('/api/calendar/1', Method.DELETE, headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.get_json(), self.DEFAULT_EVENT.to_dict())

    def test_create_event_fail_game(self):
        data = json.dumps({
            'name': 'name',
            'date': datetime.now().isoformat(),
            'note': 'note'
        })
        headers = {'Authorization': self.DEFAULT_TOKEN}
        response = self.request('/api/calendar', Method.POST, headers, data)
        self.assertEqual(response.status_code, 400)

    def test_create_event_fail_name(self):
        data = json.dumps({
            'game': 'game',
            'date': datetime.now().isoformat(),
            'note': 'note'
        })
        headers = {'Authorization': self.DEFAULT_TOKEN}
        response = self.request('/api/calendar', Method.POST, headers, data)
        self.assertEqual(response.status_code, 400)

    def test_create_event_fail_date(self):
        data = json.dumps({
            'name': 'name',
            'game': 'game',
            'note': 'note'
        })
        headers = {'Authorization': self.DEFAULT_TOKEN}
        response = self.request('/api/calendar', Method.POST, headers, data)
        self.assertEqual(response.status_code, 400)

    def test_create_event_fail_note(self):
        data = json.dumps({
            'name': 'name',
            'game': 'game',
            'date': datetime.now().isoformat(),
        })
        headers = {'Authorization': self.DEFAULT_TOKEN}
        response = self.request('/api/calendar', Method.POST, headers, data)
        self.assertEqual(response.status_code, 400)

    def test_create_event(self):
        response = self.create_event('name', 'game', datetime.now().isoformat(), 'note', self.DEFAULT_TOKEN)
        self.assertEqual(response.status_code, 201)

    def test_edit_name(self):
        data = self.DEFAULT_EVENT.to_dict()
        data['name'] = 'edit'
        headers = {'Authorization': self.DEFAULT_TOKEN}
        response = self.request(f'/api/calendar/1',
                                Method.PATCH,
                                headers=headers,
                                data=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'edit')
        

    def test_edit_game(self):
        data = self.DEFAULT_EVENT.to_dict()
        data['game'] = 'edit'
        headers = {'Authorization': self.DEFAULT_TOKEN}
        response = self.request(f'/api/calendar/1',
                                Method.PATCH,
                                headers=headers,
                                data=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['game'], 'edit')
        

    def test_edit_date(self):
        data = self.DEFAULT_EVENT.to_dict()
        date = datetime.now().isoformat()
        data['date'] = date
        headers = {'Authorization': self.DEFAULT_TOKEN}
        response = self.request(f'/api/calendar/1',
                                Method.PATCH,
                                headers=headers,
                                data=json.dumps(data))
        datea = datea.split('.')[0][:-3].split('T')
        datea = datea[0] + ' ' + datea[1]
        dateb = response.json['date']
        dateb = dateb.split('.')[0][:-3].split('T')
        dateb = dateb[0] + ' ' + dateb[1]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(dateb, datea)
        

    def test_edit_note(self):
        data = self.DEFAULT_EVENT.to_dict()
        data['note'] = 'edit'
        headers = {'Authorization': self.DEFAULT_TOKEN}
        response = self.request(f'/api/calendar/1',
                                Method.PATCH,
                                headers=headers,
                                data=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['note'], 'edit')
        
