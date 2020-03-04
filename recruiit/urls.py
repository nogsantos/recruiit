from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title='Recruiit API',
        description='Workflow para análise e seleção de candidatos API',
        default_version='v1',
    ),
    public=True,
)

v1 = 'api/v1'

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
    path(f'{v1}/', include('core.urls'), name='core'),
]
