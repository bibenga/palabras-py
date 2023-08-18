from django.urls import path, include
from rest_framework import routers, permissions, urls as rest_framework_urls
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view as get_schema_view_yasg
from drf_yasg import openapi

from . import views

schema_view_yasg = get_schema_view_yasg(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = routers.DefaultRouter()
router.register("studying", views.StudyingViewSet, "studying")

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.loginOrRegister, name="login"),
    path("studying", views.studying, name="studying"),
    path("studying2", views.studying_htmx, name="studying_htmx"),

    path('api/openapi.yml',
         get_schema_view(
             title="SlAprender",
             description="",
             version="0.1",
             permission_classes=(permissions.AllowAny,),
         ),
         name='openapi-schema'),
    path('api/swagger.html',
         TemplateView.as_view(
             template_name='slui/swagger.html',
             extra_context={'schema_url': 'openapi-schema'}
         ),
         name='swagger'),

    path('api/yasg/swagger<format>/',
         schema_view_yasg.without_ui(cache_timeout=0),
         name='schema-json'),
    path('api/yasg/swagger/',
         schema_view_yasg.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('api/yasg/redoc/',
         schema_view_yasg.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),

    path("api/", include(rest_framework_urls)),
    path("api/", include((router.urls, "slapi"))),
]
