import random
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.http import Http404
from rest_framework.viewsets import ViewSetMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from slfrase.models import TextPair, StudyState
from slui.serializers import StudyingSerializer


class StudyingViewSet(ViewSetMixin, APIView):
    serializer_class = StudyingSerializer

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer_context(self):
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self
        }

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_object(self, ignore_text_pair_id=None):
        user = self.request.user
        state_qs = StudyState.objects.filter(
            text_pair__user=user,
            is_passed_flg=False,
            is_skipped_flg=False,
        ).select_related(
            "text_pair"
        ).order_by("created_ts")
        obj = state_qs.last()
        if obj == None:
            text_pair_qs = TextPair.objects.filter(
                user=user
            ).order_by("?")
            text_pair = None
            if ignore_text_pair_id is not None:
                text_pair = text_pair_qs.exclude(
                    pk=ignore_text_pair_id
                ).first()
            if text_pair is None:
                text_pair = text_pair_qs.first()
            if text_pair is None:
                raise Http404
            if random.random() <= 0.5:
                question = text_pair.text1
                possible_answers = text_pair.text2
            else:
                question = text_pair.text2
                possible_answers = text_pair.text1
            question = TextPair.get_text_list(question)[0]
            obj = StudyState.objects.create(
                text_pair=text_pair,
                question=question,
                possible_answers=possible_answers,
            )
        if state_qs.count() > 1:
            state_qs.exclude(
                pk=obj.pk
            ).update(
                is_skipped_flg=True,
                passed_ts=timezone.now(),
            )
        return obj

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = self.request.user
        state_qs = StudyState.objects.filter(
            text_pair__user=user,
            text_pair__is_learned_flg=False,
            is_passed_flg=False,
            is_skipped_flg=False,
        ).select_related(
            "text_pair"
        ).order_by("created_ts")
        obj = state_qs.last()
        if obj:
            state_qs.update(
                is_skipped_flg=True,
                passed_ts=timezone.now(),
            )
            instance = self.get_object(ignore_text_pair_id=obj.text_pair_id)
        else:
            instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)

    @transaction.atomic
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=["PUT"], url_path="i-know", detail=True)
    @transaction.atomic
    def iKnow(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_skipped_flg = True
        instance.save()
        text_pair = instance.text_pair
        text_pair.is_learned_flg = True
        text_pair.save()
        return Response()


@require_GET
@login_required
def index(request):
    return render(request, "slui/index.html")


@require_GET
@login_required
def register(request):
    return render(request, "slui/register.html")


@require_GET
@login_required
def studying(request):
    # user = cast(AbstractUser, request.user)
    return render(request, "slui/studying.html", {
        "CSRF_COOKIE_NAME": settings.CSRF_COOKIE_NAME,
        "CSRF_HEADER_NAME": settings.CSRF_HEADER_NAME,
    })
