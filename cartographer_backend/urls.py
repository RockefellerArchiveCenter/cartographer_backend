from asterism.views import PingView
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers

from maps.views import (ArrangementMapComponentViewset, ArrangementMapViewset,
                        DeletedArrangementMapView, FindByURIView,
                        ResourceFetcherView)

router = routers.DefaultRouter()
router.register(r'maps', ArrangementMapViewset, 'arrangementmap')
router.register(r'components', ArrangementMapComponentViewset, 'arrangementmapcomponent')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('status/', PingView.as_view(), name='ping'),
    path('api/', include(router.urls)),
    path('api/delete-feed/', DeletedArrangementMapView.as_view(), name='delete-feed'),
    path('api/find-by-uri/', FindByURIView.as_view(), name='find-by-uri'),
    re_path(r'api/fetch-resource/(?P<resource_id>\d+)$', ResourceFetcherView.as_view(), name='fetch-resource')
]
