from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from tastypie.test import ResourceTestCase
from tables.models import my_models
import datetime

def get_model_by_name(models, name):
    for model in models:
        if model.model_name == name:
            return model
    return None


class PageTest(TestCase):

    def test_home_page_available(self):
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)

        for model in my_models:
            self.assertContains(response, model.verbose_name)

class ModelTest(TestCase):
    fixtures = ['tables.yaml']

    def test_model_rooms(self):

        users_model = get_model_by_name(my_models, 'users')
        rooms_model = get_model_by_name(my_models, 'rooms')

        self.assertEqual(users_model.verbose_name, 'Пользователи')
        self.assertEqual(users_model.objects.count(), 2)
        self.assertEqual(users_model.objects.get(name="af").paycheck, 536)
        self.assertEqual(users_model.objects.get(name="af").date_joined, datetime.date(2014, 5, 15))
        self.assertEqual(users_model.objects.get(name="sdfg").paycheck, 500)
        self.assertEqual(users_model.objects.get(name="sdfg").date_joined, datetime.date(2014, 5, 9))

        self.assertEqual(rooms_model.verbose_name, 'Комнаты')
        self.assertEqual(rooms_model.objects.count(), 2)
        self.assertEqual(rooms_model.objects.get(department="asdf").spots, 564)
        self.assertEqual(rooms_model.objects.get(department="sdfsa").spots, 543)

class ViewTest(TestCase):

    def test_view_url(self):
        client = Client()
        response = client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

class JsonTest(ResourceTestCase):
    fixtures = ['tables.yaml']

    def test_schema(self):
        resp = self.api_client.get('/api/tables/users/schema/', format='json')
        dresp = self.deserialize(resp)

        self.assertValidJSONResponse(resp)

        self.assertListEqual(dresp['allowed_detail_http_methods'], ["get", "post", "put", "delete", "patch"])
        self.assertListEqual(dresp['allowed_list_http_methods'], ["get", "post", "put", "delete", "patch"])

        fields_keys = ["date_joined", "field_order", "fields_verbos_name", "id", "name", "paycheck", "resource_uri"]
        self.assertEqual(len(dresp['fields']), len(fields_keys))
        self.assertKeys(dresp['fields'], fields_keys)

        self.assertDictEqual(dresp['fields']['field_order'], {"0": "name", "1": "paycheck", "2": "date_joined"})



        resp = self.api_client.get('/api/tables/rooms/schema/', format='json')
        dresp = self.deserialize(resp)

        self.assertValidJSONResponse(resp)

        self.assertListEqual(dresp['allowed_detail_http_methods'], ["get", "post", "put", "delete", "patch"])
        self.assertListEqual(dresp['allowed_list_http_methods'], ["get", "post", "put", "delete", "patch"])

        fields_keys = ["department", "field_order", "fields_verbos_name", "id", "resource_uri", "spots"]
        self.assertEqual(len(dresp['fields']), len(fields_keys))
        self.assertKeys(dresp['fields'], fields_keys)

        self.assertDictEqual(dresp['fields']['field_order'], {"0": "spots", "1": "department"})

    def test_get_json(self):
        resp = self.api_client.get('/api/tables/users/', format='json')
        dresp = self.deserialize(resp)

        self.assertValidJSONResponse(resp)

        self.assertEqual(len(dresp['objects']), 2)

        users = {}
        users[0] = {
            "date_joined": "2014-05-15",
            "id": 2, "name": "af",
            "paycheck": 536,
            "resource_uri": "/api/tables/users/2/"}
        users[1] = {
            "date_joined": "2014-05-09",
            "id": 4, "name": "sdfg",
            "paycheck": 500,
            "resource_uri": "/api/tables/users/4/"}

        self.assertDictEqual(dresp['objects'][0], users[0])
        self.assertDictEqual(dresp['objects'][1], users[1])


        resp = self.api_client.get('/api/tables/rooms/', format='json')
        dresp = self.deserialize(resp)

        self.assertValidJSONResponse(resp)

        self.assertEqual(len(dresp['objects']), 2)

        users = {}
        users[0] = {
            "department": "asdf", "id": 2,
            "resource_uri": "/api/tables/rooms/2/", "spots": 564}
        users[1] = {
            "department": "sdfsa", "id": 3,
            "resource_uri": "/api/tables/rooms/3/", "spots": 543}

        self.assertDictEqual(dresp['objects'][0], users[0])
        self.assertDictEqual(dresp['objects'][1], users[1])

    def test_post_json(self):
        users_model = get_model_by_name(my_models, 'users')
        rooms_model = get_model_by_name(my_models, 'rooms')

        post_data = {
            "date_joined": "2000-05-15",
            "name": "test",
            "paycheck": 100}
        self.assertEqual(users_model.objects.count(), 2)
        self.assertHttpCreated(self.api_client.post('/api/tables/users/', format='json', data=post_data))
        self.assertEqual(users_model.objects.count(), 3)

        post_data = {"department": "Test room", "spots": 123}
        self.assertEqual(rooms_model.objects.count(), 2)
        self.assertHttpCreated(self.api_client.post('/api/tables/rooms/', format='json', data=post_data))
        self.assertEqual(rooms_model.objects.count(), 3)

    def test_update_json(self):
        users_model = get_model_by_name(my_models, 'users')
        rooms_model = get_model_by_name(my_models, 'rooms')

        post_data = {
            "date_joined": "2014-05-16",
            "id": 2, "name": "new Name",
            "paycheck": 1000,}
        self.assertEqual(users_model.objects.count(), 2)
        self.assertHttpCreated(self.api_client.post('/api/tables/users/', format='json', data=post_data))
        self.assertEqual(users_model.objects.count(), 2)

        resp = self.api_client.get('/api/tables/users/2/', format='json')
        dresp = self.deserialize(resp)

        self.assertValidJSONResponse(resp)

        user = {
            "date_joined": "2014-05-16",
            "id": 2, "name": "new Name",
            "paycheck": 1000,
            "resource_uri": "/api/tables/users/2/"}
        self.assertDictEqual(dresp, user)


        post_data = {"department": "New department", "id": 2, "spots": 10}
        self.assertEqual(rooms_model.objects.count(), 2)
        self.assertHttpCreated(self.api_client.post('/api/tables/rooms/', format='json', data=post_data))
        self.assertEqual(rooms_model.objects.count(), 2)

        resp = self.api_client.get('/api/tables/rooms/2/', format='json')
        dresp = self.deserialize(resp)

        self.assertValidJSONResponse(resp)

        room = {"department": "New department", "id": 2,
                "resource_uri": "/api/tables/rooms/2/", "spots": 10}
        self.assertDictEqual(dresp, room)

    def test_del_json(self):
        users_model = get_model_by_name(my_models, 'users')
        rooms_model = get_model_by_name(my_models, 'rooms')


        self.assertEqual(users_model.objects.count(), 2)
        self.assertHttpAccepted(self.api_client.delete('/api/tables/users/2/', format='json'))
        self.assertEqual(users_model.objects.count(), 1)

        self.assertEqual(rooms_model.objects.count(), 2)
        self.assertHttpAccepted(self.api_client.delete('/api/tables/rooms/3/', format='json'))
        self.assertEqual(rooms_model.objects.count(), 1)
