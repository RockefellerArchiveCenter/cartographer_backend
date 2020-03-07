import random
import string

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from .models import (ArrangementMap, ArrangementMapComponent,
                     DeletedArrangementMap)
from .serializers import ArrangementMapSerializer
from .views import (ArrangementMapComponentViewset, ArrangementMapViewset,
                    FindByIdView)


def get_title_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10))


class CartographerTest(TestCase):
    def setUp(self):
        self.map_number = random.randint(2, 10)
        self.component_number = random.randint(2, 20)
        self.client = Client()
        self.factory = APIRequestFactory()

    def create_maps(self):
        for i in range(self.map_number):
            request = self.factory.post(reverse('arrangementmap-list'), format="json", data={'title': get_title_string()})
            response = ArrangementMapViewset.as_view(actions={"post": "create"})(request)
            self.assertEqual(response.status_code, 201, "Wrong HTTP status code")
        self.assertEqual(len(ArrangementMap.objects.all()), self.map_number, "Wrong number of instances created")
        for map in ArrangementMap.objects.all():
            self.assertEqual(map.publish, False, "Map was set to publish.")

    def create_components(self):
        map = random.choice(ArrangementMap.objects.all())
        for i in range(self.component_number):
            request = self.factory.post(
                reverse('arrangementmapcomponent-list'),
                format="json",
                data={
                    'title': get_title_string(),
                    'archivesspace_uri': get_title_string(length=15),
                    'map': map.pk})
            response = ArrangementMapComponentViewset.as_view(actions={"post": "create"})(request)
            self.assertEqual(response.status_code, 201, "Error creating component: {}".format(response.data))
        self.assertEqual(
            len(ArrangementMapComponent.objects.all()),
            self.component_number,
            "Expecting {} ArrangementMapComponent objects but got {}".format(
                self.component_number, len(ArrangementMapComponent.objects.all())))

    def edit_maps(self):
        map = random.choice(ArrangementMap.objects.all())
        title = get_title_string(20)
        map.title = title
        serializer = ArrangementMapSerializer(map)
        request = self.factory.put(reverse('arrangementmap-detail', kwargs={"pk": map.pk}), format="json", data=serializer.data)
        response = ArrangementMapViewset.as_view(actions={"put": "update"})(request, pk=map.pk)
        self.assertEqual(response.status_code, 200, "Wrong HTTP status code")
        map.refresh_from_db()
        self.assertEqual(title, map.title, "Title was not updated")
        self.assertEqual(len(ArrangementMap.objects.all()), self.map_number, "Edit created a new instance")
        self.assertTrue(map.created < map.modified, "Modified time was not updated")

    def delete_maps(self):
        delete_number = random.randint(1, self.map_number - 1)
        for i in range(delete_number):
            map = random.choice(ArrangementMap.objects.all())
            request = self.factory.delete(reverse('arrangementmap-detail', kwargs={"pk": map.pk}), format="json")
            response = ArrangementMapViewset.as_view(actions={"delete": "destroy"})(request, pk=map.pk)
            self.assertEqual(response.status_code, 204, "Wrong HTTP status code")
        self.assertEqual(len(ArrangementMap.objects.all()), self.map_number - delete_number, "Wrong number of instances deleted")
        self.assertEqual(len(DeletedArrangementMap.objects.all()), delete_number, "DeletedArrangementMap objects were not created on delete")

    def list_views(self):
        for view, viewset in [('arrangementmap-list', ArrangementMapViewset), ('arrangementmapcomponent-list', ArrangementMapComponentViewset)]:
            request = self.factory.get(reverse(view), format="json")
            response = viewset.as_view(actions={"get": "list"})(request)
            self.assertEqual(response.status_code, 200, "Request error: {}".format(response.data))
            request = self.factory.get('{}?modified_since={}'.format(reverse(view), random.randint(1500000000, 2500000000)), format="json")
            response = viewset.as_view(actions={"get": "list"})(request)
            self.assertEqual(response.status_code, 200, "Request error: {}".format(response.data))
            request = self.factory.get('{}?published'.format(reverse(view)), format="json")
            response = viewset.as_view(actions={"get": "list"})(request)
            self.assertEqual(response.status_code, 200, "Request error: {}".format(response.data))

    def detail_views(self):
        obj = random.choice(ArrangementMap.objects.all())
        request = self.factory.get(reverse('arrangementmap-detail', kwargs={"pk": obj.pk}), format="json")
        response = ArrangementMapViewset.as_view(actions={"get": "retrieve"})(request, pk=obj.pk)
        self.assertEqual(response.status_code, 200, "Wrong HTTP status code")

    def delete_feed_view(self):
        response = self.client.get(reverse('delete-feed'), format="json")
        self.assertEqual(response.status_code, 200, "Wrong HTTP status code")
        self.assertTrue(response.data['count'] > 0, "No deleted instances")
        time_response = self.client.get('{}?deleted_since={}'.format(reverse('delete-feed'), random.randint(1500000000, 2500000000)), format="json")
        self.assertEqual(time_response.status_code, 200, "Wrong HTTP status code")

    def find_by_id_view(self):
        map = random.choice(ArrangementMapComponent.objects.all())
        uri = map.archivesspace_uri
        request = self.factory.get("{}?uri={}".format(reverse('find-by-id'), uri), format="json")
        response = FindByIdView.as_view()(request)
        self.assertEqual(response.status_code, 200, "FindById error: {}".format(response.data))

    def schema(self):
        schema = self.client.get(reverse('schema'))
        self.assertEqual(schema.status_code, 200, "Wrong HTTP code")

    def test_maps(self):
        self.create_maps()
        self.create_components()
        self.edit_maps()
        self.list_views()
        self.detail_views()
        self.find_by_id_view()
        self.delete_maps()
        self.delete_feed_view()
        self.schema()
