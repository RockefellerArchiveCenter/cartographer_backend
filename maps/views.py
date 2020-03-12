from datetime import datetime

from asnake.aspace import ASpace
from asnake.jsonmodel import JSONModelObject
from cartographer_backend import settings
from django.core.exceptions import FieldError
from django.utils.timezone import make_aware
from rest_framework.exceptions import ParseError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import (ArrangementMap, ArrangementMapComponent,
                     DeletedArrangementMap)
from .serializers import (ArrangementMapComponentListSerializer,
                          ArrangementMapComponentSerializer,
                          ArrangementMapListSerializer,
                          ArrangementMapSerializer,
                          DeletedArrangementMapSerializer)


def process_params(view):
    """Filters querysets based on parameters.

    If `last_modified` is present, only returns objects which have been modified
    since that timestamp.

    If `published` is present, only returns ArrangementMaps which have been
    explicitly published or ArrangementMapComponents which belong to a published
    map.
    """
    modified_since = int(view.request.query_params.get('modified_since', 0))
    queryset = view.model.objects.filter(
        modified__gte=make_aware(datetime.fromtimestamp(modified_since))).order_by('-modified')
    if 'published' in view.request.query_params:
        try:
            queryset.exclude(publish=False)
        except FieldError:
            queryset.exclude(map__publish=False)
    return queryset


class ArrangementMapViewset(ModelViewSet):
    """ArrangementMap endpoints.

    retrieve:
        Returns data about an ArrangementMap object, identified by a primary key.

    list:
        Returns paginated data about all ArrangementMap objects. Allows for two

        URL parameters:
            `modified_since` - only returns records modified after this time
                (formatted as a UTC timestamp)
            `published` - returns only published ArrangementMap objects
    """
    model = ArrangementMap

    def get_serializer_class(self):
        if self.action == 'list':
            return ArrangementMapListSerializer
        return ArrangementMapSerializer

    def get_queryset(self):
        return process_params(self)


class ArrangementMapComponentViewset(ModelViewSet):
    """ArrangementMapComponent endpoints.

    retrieve:
        Returns data about an ArrangementMapComponent object, identified by a primary key.

    list:
        Returns paginated data about all ArrangementMapComponent objects.

        URL parameters:
            `modified_since` - only returns records modified after this time
                (formatted as a UTC timestamp)
            `published` - returns only published ArrangementMap objects
    """
    model = ArrangementMapComponent
    queryset = ArrangementMapComponent.objects.all().order_by('-modified')

    def get_serializer_class(self):
        if self.action == 'list':
            return ArrangementMapComponentListSerializer
        return ArrangementMapComponentSerializer

    def get_queryset(self):
        return process_params(self)


class DeletedArrangementMapView(ListAPIView):
    """Returns deleted ArrangementMap and ArrangementMapComponent objects.

    list:
        Return paginated data about all Deleted ArrangementMap Objects.

    Params:
        deleted_since (timestamp): an optional argument which limits return to
            objects deleted since.
    """
    model = DeletedArrangementMap
    serializer_class = DeletedArrangementMapSerializer

    def get_queryset(self):
        deleted_since = int(self.request.query_params.get('deleted_since', 0))
        return DeletedArrangementMap.objects.filter(
            deleted__gte=make_aware(datetime.fromtimestamp(deleted_since))).order_by('-deleted')


class ResourceFetcherView(APIView):
    """Fetches a resource from ArchivesSpace which matches a given ID.

    Params:
        resource_id (int): an ArchivesSpace identifier for a resource record.
    """

    def get(self, request, *args, **kwargs):
        try:
            self.repo = ASpace(baseurl=settings.ASPACE['baseurl'],
                               username=settings.ASPACE['username'],
                               password=settings.ASPACE['password']).repositories(settings.ASPACE['repo_id'])
            resource = self.repo.resources(kwargs.get('resource_id'))
            if isinstance(resource, JSONModelObject):
                return Response(resource.json(), status=200)
            return Response(resource['error'], status=404)
        except Exception as e:
            return Response(str(e), status=500)


class FindByURIView(ListAPIView):
    """Returns all ArrangementMapComponent objects whose `archivesspace_uri`
    property matches a sumitted URI.

    Params:
        uri (str): an ArchivesSpace URI
    """
    model = ArrangementMapComponent
    serializer_class = ArrangementMapComponentSerializer

    def get_queryset(self):
        try:
            uri = self.request.GET["uri"]
            return ArrangementMapComponent.objects.filter(archivesspace_uri=uri)
        except KeyError:
            raise ParseError("Required URL parameter `uri` missing.")
