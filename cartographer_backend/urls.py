from django.contrib import admin
from django.urls import include, path, re_path
from maps.views import (ArrangementMapComponentViewset, ArrangementMapViewset,
                        DeletedArrangementMapView, FindByURIView,
                        ResourceFetcherView)
from rest_framework import routers
from rest_framework.schemas import get_schema_view

router = routers.DefaultRouter()
router.register(r'maps', ArrangementMapViewset, 'arrangementmap')
router.register(r'components', ArrangementMapComponentViewset, 'arrangementmapcomponent')

schema_view = get_schema_view(
    title="Cartographer API",
    description="Endpoints for Cartographer application."
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('status/', include('health_check.api.urls')),
    re_path(r'^schema/', schema_view, name='schema'),
    path('api/', include(router.urls)),
    path('api/delete-feed/', DeletedArrangementMapView.as_view(), name='delete-feed'),
    path('api/find-by-uri/', FindByURIView.as_view(), name='find-by-uri'),
    re_path(r'api/fetch-resource/(?P<resource_id>\d+)$', ResourceFetcherView.as_view(), name='fetch-resource')
]
