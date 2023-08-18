import random
from django import forms
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.utils import timezone
from django.db import transaction
from django.http import Http404, HttpResponse
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


@sensitive_post_parameters()
@csrf_protect
@never_cache
def loginOrRegister(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)

        if form.is_valid():
            user = form.get_user()
            print(user)
            if user is not None:
                login(request, user)
                # response = redirect("studying")
                # response['HX-Redirect'] = response['Location']
                response = HttpResponse()
                response['HX-Location'] = request.build_absolute_uri(
                    reverse('studying'))
                return response
            else:
                # No backend authenticated the credentials
                ...

        return render(request, "slui/register-form.html", {"form": form})

    else:
        form = AuthenticationForm(request)
        return render(request, "slui/register.html", {"form": form})


@require_GET
@login_required
def studying(request):
    # user = cast(AbstractUser, request.user)
    return render(request, "slui/studying.html", {
        "CSRF_COOKIE_NAME": settings.CSRF_COOKIE_NAME,
        "CSRF_HEADER_NAME": settings.CSRF_HEADER_NAME,
    })


class AnswerForm(forms.ModelForm):
    answer = forms.CharField(widget=forms.TextInput(attrs={"autofocus": True}))

    class Meta:
        model = StudyState
        fields = ['answer']

    def clean_answer(self):
        answer = self.cleaned_data["answer"]

        answer = TextPair.get_words(answer.lower())
        variants = [TextPair.get_words(x.lower())
                    for x in TextPair.get_text_list(self.instance.possible_answers)]

        is_passed_flg = answer in variants
        if not is_passed_flg:
            raise forms.ValidationError("La respuesta es incorrecta.")

        return answer

@login_required
@transaction.atomic
def studying_htmx(request):
    user = request.user

    def get_state():
        state_qs = StudyState.objects.filter(
            text_pair__user=user,
            is_passed_flg=False,
            is_skipped_flg=False,
        ).select_related(
            "text_pair"
        ).order_by("created_ts")
        state = state_qs.last()
        if state == None:
            text_pair_qs = TextPair.objects.filter(
                user=user
            ).order_by("?")
            text_pair = None
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
            state = StudyState.objects.create(
                text_pair=text_pair,
                question=question,
                possible_answers=possible_answers,
            )
        if state_qs.count() > 1:
            state_qs.exclude(
                pk=state.pk
            ).update(
                is_skipped_flg=True,
                passed_ts=timezone.now(),
            )
        return state

    state = get_state()

    if request.method == "POST":
        if "siguiente" in request.POST:
            if not state.is_skipped_flg:
                state.is_skipped_flg = True
                state.save()
            # state = get_state()
            return redirect("studying_htmx")

        elif "sé" in request.POST:
            text_pair = state.text_pair
            if not text_pair.is_learned_flg:
                text_pair.is_learned_flg = True
                text_pair.save()
            # state = get_state()
            return redirect("studying_htmx")

        else: # entregar
            form = AnswerForm(request.POST, instance=state)
            if form.is_valid():
                pass

    else:
        form = AnswerForm(instance=state)

    return render(request, "slui/studying.htmx.html", {
        "state": state,
        "form": form,
    })
