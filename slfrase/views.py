# from typing import cast
# from django.conf import settings
# from django.shortcuts import redirect, render
# from django.contrib.auth.models import AbstractUser
# from django.views.decorators.http import require_http_methods
# from django import forms
# from .models import TextPair


# def index(request):
#     user = cast("AbstractUser", request.user)
#     if user.is_authenticated:
#         pass
#     else:
#         pass
#     return render(request, "slfrase/index.html", {
#     })


# @require_http_methods(["GET", "POST"])
# def register(request):
#     user = cast("AbstractUser", request.user)
#     if user.is_authenticated:
#         return redirect(index)

#     return render(request, "slfrase/register.html", {
#     })


# class StudyingForm(forms.Form):
#     # phrase = forms.IntegerField(widget=forms.HiddenInput)
#     state = forms.ChoiceField(
#         choices=(("INIT", "INIT"), ("EXAM", "EXAM"), ("DONE", "DONE")),
#         widget=forms.HiddenInput)
#     phrase = forms.ModelChoiceField(
#         widget=forms.HiddenInput,
#         queryset=TextPair.objects.all())
#     direction = forms.ChoiceField(
#         choices=(("1->2", "1->2"), ("2->1", "2->1")),
#         widget=forms.HiddenInput)
#     # answer = forms.CharField(widget=forms.Textarea)
#     answer = forms.CharField(widget=forms.TextInput({"autofocus": True}))

#     def __init__(self, *args, user=None, **kwargs) -> None:
#         super().__init__(*args, **kwargs)
#         self.user = user

#     # def clean_answer(self):
#     #     phrase = self.cleaned_data["phrase"]
#     #     answer = self.cleaned_data["answer"]
#     #     variants = [x.lower() for x in phrase.text2_list]
#     #     if answer not in variants:
#     #         raise forms.ValidationError("Answer is incorrect!")
#     #     return answer

#     def clean(self):
#         data = super().clean()

#         phrase = data["phrase"]
#         answer = data["answer"]
#         answer = phrase.get_words(answer.lower())
#         variants = [phrase.get_words(x.lower()) for x in phrase.text2_list]
#         # import pprint
#         # pprint.pprint(answer)
#         # pprint.pprint(variants)
#         if answer not in variants:
#             data["state"] = "EXAM"
#             self.data = self.data.copy()
#             self.data["state"] = "EXAM"
#             raise forms.ValidationError({"answer": "Answer is incorrect!"})
#         else:
#             self.data = self.data.copy()
#             self.data["state"] = "DONE"

#         return data


# @require_http_methods(["GET", "POST"])
# def studying(request):
#     user = cast(AbstractUser, request.user)
#     if not user.is_authenticated:
#         return redirect(index)

#     # state = "INIT"
#     if request.method == "POST":
#         form = StudyingForm(request.POST, user=user)
#         if form.is_valid():
#             state = form.cleaned_data["state"]
#             if state == "DONE":
#                 return redirect(studying)
#         phrase: TextPair = form.cleaned_data["phrase"]

#     else:
#         phrase = TextPair.objects.filter(
#             user=user,
#             is_learned_flg=False
#         ).order_by("?").first()
#         form = StudyingForm(
#             initial={
#                 "state": "INIT",
#                 "phrase": phrase.pk,
#                 "direction": "1->2"
#             },
#             user=user
#         )

#     return render(request, "slfrase/studying.html", {
#         # "state": state,
#         "phrase": phrase,
#         "form": form,
#         "CSRF_COOKIE_NAME": settings.CSRF_COOKIE_NAME,
#         "CSRF_HEADER_NAME": settings.CSRF_HEADER_NAME,
#     })
