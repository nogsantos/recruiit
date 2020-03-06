# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import HealthCheckViewSet, FileUploadView

routers = DefaultRouter()
routers.register('', HealthCheckViewSet, base_name='core')

urlpatterns = [
    path('', include(routers.get_urls())),
    url(r'^upload/(?P<filename>[^/]+)$', FileUploadView.as_view())
]
