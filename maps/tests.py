import random
import string

import vcr
from cartographer_backend import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from .models import (ArrangementMap, ArrangementMapComponent,
                     DeletedArrangementMap)
from .serializers import (ArrangementMapComponentSerializer,
                          ArrangementMapSerializer)
from .views import (ArrangementMapComponentViewset, ArrangementMapViewset,
                    FindByURIView)

edit_vcr = vcr.VCR(
    serializer='json',
    cassette_library_dir='maps/fixtures/cassettes',
    record_mode='once',
    match_on=['path', 'method'],
    filter_query_parameters=['username', 'password'],
    filter_headers=['Authorization'],
    filter_post_data_parameters=['password']
)


def get_title_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10))


class CartographerTest(TestCase):
    """Tests the Cartographer backend, with a focus on API interactions."""

    fixtures = ["initial.json"]

    def setUp(self):
        self.component_number = 10
        self.factory = APIRequestFactory()

    def test_create_maps(self):
        """Test creation of ArrangementMap objects."""
        ArrangementMap.objects.all().delete()
        request = self.factory.post(
            reverse('arrangementmap-list'), format="json",
            data={'title': get_title_string(), 'level': get_title_string(length=5)})
        response = ArrangementMapViewset.as_view(actions={"post": "create"})(request)
        self.assertEqual(response.status_code, 201, "Wrong HTTP status code")
        self.assertEqual(len(ArrangementMap.objects.all()), 1, "Wrong number of instances created")
        for map in ArrangementMap.objects.all():
            self.assertEqual(map.publish, False, "Map was incorrectly set to publish.")

    def test_create_components(self):
        """Tests creation of ArrangementMapComponent objects."""
        with edit_vcr.use_cassette("create-components.json"):
            ArrangementMapComponent.objects.all().delete()
            map = random.choice(ArrangementMap.objects.all())
            for i in range(self.component_number):
                request = self.factory.post(
                    reverse('arrangementmapcomponent-list'),
                    format="json",
                    data={
                        'title': get_title_string(),
                        'archivesspace_uri': f"/repositories/{settings.ASPACE['repo_id']}/resources/1",
                        'level': random.choice(['collection', 'series', 'subseries']),
                        'map': map.pk,
                        'order': i})
                response = ArrangementMapComponentViewset.as_view(actions={"post": "create"})(request)
                self.assertEqual(response.status_code, 201, "Error creating component: {response.data}")
            self.assertEqual(
                len(ArrangementMapComponent.objects.all()),
                self.component_number,
                f"Expecting {self.component_number} ArrangementMapComponent objects but got {len(ArrangementMapComponent.objects.all())}")

    def test_edit_objects(self):
        """Tests editing of ArrangementMap objects."""
        for model, serializer, view, viewset in [
                (ArrangementMap, ArrangementMapSerializer, "arrangementmap-detail", ArrangementMapViewset),
                (ArrangementMapComponent, ArrangementMapComponentSerializer, "arrangementmapcomponent-detail", ArrangementMapComponentViewset)]:
            with edit_vcr.use_cassette(f"edit-{view}.json"):
                obj = random.choice(model.objects.all())
                title = get_title_string(20)
                obj.title = title
                serializer = serializer(obj)
                request = self.factory.put(reverse(view, kwargs={"pk": obj.pk}), format="json", data=serializer.data)
                response = viewset.as_view(actions={"put": "update"})(request, pk=obj.pk)
                self.assertEqual(response.status_code, 200, f"Error editing {model}: {response.data}")
                obj.refresh_from_db()
                self.assertEqual(title, obj.title, "Title was not updated")
                self.assertTrue(obj.created < obj.modified, "Modified time was not updated")

    def test_delete_maps(self):
        """Tests deletion of ArrangementMap objects."""
        delete_number = 1
        for i in range(delete_number):
            map = random.choice(ArrangementMap.objects.all())
            delete_number += len(ArrangementMapComponent.objects.filter(map=map))
            request = self.factory.delete(reverse("arrangementmap-detail", kwargs={"pk": map.pk}), format="json")
            response = ArrangementMapViewset.as_view(actions={"delete": "destroy"})(request, pk=map.pk)
            self.assertEqual(response.status_code, 204, "Wrong HTTP status code")
        self.assertEqual(
            len(DeletedArrangementMap.objects.all()),
            delete_number,
            "DeletedArrangementMap objects were not created on delete")

    def test_list_views(self):
        """Tests list views for ArrangementMap and ArrangementMapComponent objects."""
        for view, viewset in [('arrangementmap-list', ArrangementMapViewset), ('arrangementmapcomponent-list', ArrangementMapComponentViewset)]:
            request = self.factory.get(reverse(view), format="json")
            response = viewset.as_view(actions={"get": "list"})(request)
            self.assertEqual(response.status_code, 200, f"Request error: {response.data}")
            request = self.factory.get(f'{reverse(view)}?modified_since={random.randint(1500000000, 2500000000)}', format="json")
            response = viewset.as_view(actions={"get": "list"})(request)
            self.assertEqual(response.status_code, 200, f"Request error: {response.data}")
            request = self.factory.get(f'{view}?published', format="json")
            response = viewset.as_view(actions={"get": "list"})(request)
            self.assertEqual(response.status_code, 200, f"Request error: {response.data}")

    def test_detail_views(self):
        """Tests detail views for ArrangementMap and ArrangementMapComponent objects."""
        for model, view, viewset in [
                (ArrangementMap, 'arrangementmap-detail', ArrangementMapViewset),
                (ArrangementMapComponent, 'arrangementmapcomponent-detail', ArrangementMapComponentViewset)]:
            for obj in model.objects.all():
                request = self.factory.get(reverse(view, kwargs={"pk": obj.pk}), format="json")
                response = viewset.as_view(actions={"get": "retrieve"})(request, pk=obj.pk)
                self.assertEqual(response.status_code, 200, f"Error in {model} detail view: {response.data}")
                self.assertIsNot(response.data.get("id"), None, "`id` key missing from response.")

    def test_delete_feed_view(self):
        """Tests DeleteFeed views."""
        ArrangementMapComponent.objects.all().delete()
        response = self.client.get(reverse('delete-feed'), format="json")
        self.assertEqual(response.status_code, 200, "Wrong HTTP status code")
        self.assertTrue(response.data['count'] > 0, "No deleted instances")
        for obj in response.data["results"]:
            self.assertIsNot(obj.get("ref"), None)
            if "components" in obj.get("ref"):
                self.assertIsNot(obj.get("archivesspace_uri"), None)
        time_response = self.client.get(
            f"{reverse('delete-feed')}?deleted_since={random.randint(1500000000, 2500000000)}",
            format="json")
        self.assertEqual(time_response.status_code, 200, "Wrong HTTP status code")

    def test_find_by_uri_view(self):
        """Tests FindByURIView."""
        map = random.choice(ArrangementMapComponent.objects.all())
        uri = map.archivesspace_uri
        request = self.factory.get(f"{reverse('find-by-uri')}?uri={uri}", format="json")
        response = FindByURIView.as_view()(request)
        self.assertEqual(response.status_code, 200, f"FindByURI error: {response.data}")
        self.assertTrue(
            response.data["count"] >= 1,
            f"Response count is {response.data['count']}, should have been at least 1")

    def test_objects_before_view(self):
        """Tests objects_before action view"""
        obj = random.choice(ArrangementMapComponent.objects.all())
        request = self.factory.get(reverse("arrangementmapcomponent-objects-before", args=[obj.pk]), format="json")
        response = ArrangementMapComponentViewset.as_view(actions={"get": "objects_before"})(request, pk=obj.pk)
        self.assertEqual(response.status_code, 200, f"Error in objects_before action view: {response.data}")
        self.assertTrue(isinstance(response.data["count"], int))

    def test_resource_fetcher_view(self):
        """Tests ResourceFetcherView."""
        with edit_vcr.use_cassette("resource-fetcher.json"):
            found = self.client.get(reverse("fetch-resource", kwargs={"resource_id": 1}))
            self.assertEqual(found.status_code, 200)
            self.assertTrue(isinstance(found.json(), dict))
            not_found = self.client.get(reverse("fetch-resource", kwargs={"resource_id": 12345}))
            self.assertEqual(not_found.status_code, 404)
            self.assertTrue(isinstance(not_found.json(), str))

    def test_schema(self):
        """Tests OpenAPI schema view."""
        schema = self.client.get(reverse('schema'))
        self.assertEqual(schema.status_code, 200, "Wrong HTTP code")
