from datetime import datetime

from asnake.aspace import ASpace
from asnake.jsonmodel import JSONModelObject
from django.utils.timezone import make_aware
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from cartographer_backend import settings
from .models import ArrangementMap, ArrangementMapComponent, DeletedArrangementMap
from .serializers import *


class ArrangementMapViewset(ModelViewSet):
    """
    retrieve:
    Return data about an ArrangementMap object, identified by a primary key.

    list:
    Return paginated data about all ArrangementMap objects. Allows for two
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
        modified_since = int(self.request.query_params.get('modified_since', 0))
        if 'published' in self.request.query_params:
            return ArrangementMap.objects.filter(modified__gte=make_aware(datetime.fromtimestamp(modified_since)), publish=True).order_by('-modified')
        return ArrangementMap.objects.filter(modified__gte=make_aware(datetime.fromtimestamp(modified_since))).order_by('-modified')


class ArrangementMapComponentViewset(ModelViewSet):
    """
    retrieve:
    Return data about an ArrangementMapComponent object, identified by a primary key.

    list:
    Return paginated data about all ArrangementMapComponent objects.
    """
    model = ArrangementMapComponent
    queryset = ArrangementMapComponent.objects.all().order_by('-modified')

    def get_serializer_class(self):
        if self.action == 'list':
            return ArrangementMapComponentListSerializer
        return ArrangementMapComponentSerializer


class DeletedArrangementMapView(ListAPIView):
    """
    list:
    Return paginated data about all Deleted ArrangementMap Objects.
    """
    model = DeletedArrangementMap
    serializer_class = DeletedArrangementMapSerializer

    def get_queryset(self):
        deleted_since = int(self.request.query_params.get('deleted_since', 0))
        return DeletedArrangementMap.objects.filter(deleted__gte=make_aware(datetime.fromtimestamp(deleted_since))).order_by('-deleted')


class ResourceFetcherView(APIView):

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
