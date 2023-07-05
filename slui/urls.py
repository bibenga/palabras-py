from django.urls import path, include
from rest_framework import routers, urls as rest_framework_urls
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView

from . import views

router = routers.DefaultRouter()
router.register("studying", views.StudyingViewSet, "studying")

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("studying", views.studying, name="studying"),

    path('api/openapi.yml',
         get_schema_view(
             title="SlAprender",
             description="",
             version="0.1"
         ),
         name='openapi-schema'),
    path('api/swagger.html',
         TemplateView.as_view(
             template_name='slui/swagger.html',
             extra_context={'schema_url': 'openapi-schema'}
         ),
         name='swagger'),

    path("api/", include(rest_framework_urls)),
    path("api/", include((router.urls, "slapi"))),
]
