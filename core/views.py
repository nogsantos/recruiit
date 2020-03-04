# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response


class HealthCheckViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)
