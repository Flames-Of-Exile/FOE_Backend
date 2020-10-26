import json

from .setup import BasicTests, Method

from models import Pin


class PinTests(BasicTests):

    def test_list(self):
        response = self.request('/api/pins', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertIn(self.DEFAULT_PIN.to_dict(), data)

    def test_retrieve(self):
        response = self.request('/api/pins/1', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.DEFAULT_PIN.to_dict(), response.get_json())

    def test_create_success(self):
        response = self.create_pin(self.DEFAULT_TOKEN, 5, 5, Pin.Symbol.ANIMAL.value, Pin.Resource.WOLF.value, 1, 1, 1)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertDictContainsSubset({'position_x': 5.0, 'position_y': 5.0,
                                       'symbol': Pin.Symbol.ANIMAL.value, 'resource': Pin.Resource.WOLF.value}, data)

    def test_create_fail_invalid_world(self):
        response = self.create_pin(self.DEFAULT_TOKEN, 5, 5, Pin.Symbol.ANIMAL.value, Pin.Resource.WOLF.value, 2)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'violates foreign key constraint "pins_world_id_fkey"', response.data)

    def test_update(self):
        data = {
            'position_x': 2.0,
            'position_y': 2.5,
            'symbol': Pin.Symbol.GRAVE.value,
            'resource': Pin.Resource.HUMAN.value,
            'rank': 10,
            'name': 'some name',
            'amount': 4,
            'respawn': 30,
            'notes': 'some notes',
            'x_cord': 2,
            'y_cord': 2


        }
        old_pin = self.DEFAULT_PIN.to_dict()
        response = self.request('/api/pins/1', Method.PATCH, {'Authorization': self.DEFAULT_TOKEN}, json.dumps(data))
        self.assertEqual(response.status_code, 200)
        edit_details = (f"Position change from {old_pin['position_x']}/{old_pin['position_y']} "
                        f"to {data['position_x']}/{data['position_y']}\n"
                        f"Symbol changed from {old_pin['symbol']} to {data['symbol']}\n"
                        f"Resource changed from {old_pin['resource']} to {data['resource']}\n"
                        f"Rank changed from {old_pin['rank']} to {data['rank']}\n"
                        f"Name changed from {old_pin['name']} to {data['name']}\n"
                        f"Amount changed from {old_pin['amount']} to {data['amount']}\n"
                        f"Respawn changed from {old_pin['respawn']} to {data['respawn']}\n"
                        f"Notes changed from {old_pin['notes']} to {data['notes']}\n"
                        f"X Coordinate changed from {old_pin['x_cord']} to {data['x_cord']}\n"
                        f"Y Coordinate changed from {old_pin['y_cord']} to {data['y_cord']}\n")

        res_data = response.get_json()
        self.assertEqual(res_data['edits'][0]['details'], edit_details)
        self.assertEqual(res_data['edits'][0]['user']['id'], 1)
        self.assertDictContainsSubset(data, res_data)

    def test_delete(self):
        response = self.request('/api/pins/1', Method.DELETE, {'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(response.status_code, 200)
        response = self.request('/api/pins', headers={'Authorization': self.DEFAULT_TOKEN})
        self.assertEqual(len(response.get_json()), 0)
