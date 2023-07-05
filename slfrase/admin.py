from django.contrib import admin
from django import forms
from django.db import models

from slfrase.models import TextPair, StudyState


@admin.register(TextPair)
class PhraseAdmin(admin.ModelAdmin):
    model = TextPair
    list_display = ("user", "text1", "text2", "is_learned_flg")
    list_select_related = ("user", )
    search_fields = ("text1", "text2")
    actions = ("clear_is_learned_flg",)
    fields = ("user", "text1", "text2",
              "is_learned_flg", "learned_ts", "comment")
    raw_id_fields = ("user",)
    readonly_fields = ("learned_ts",)
    ordering = ("user",)
    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"rows": 4, "cols": 80})},
    }

    @admin.action()
    def clear_is_learned_flg(self, request, queryset):
        queryset.update(
            is_learned_flg=False,
            learned_ts=None,
        )


@admin.register(StudyState)
class StudyStateAdmin(admin.ModelAdmin):
    model = StudyState
    list_per_page = 20
    list_display = ("text_pair", "question", "possible_answers",
                    "is_passed_flg", "is_skipped_flg", "created_ts")
    list_select_related = ("text_pair",)
    search_fields = ("text_pair__text1", "text_pair__text2")
    fields = ("text_pair", "question", "possible_answers", "answer",
              "is_passed_flg", "is_skipped_flg", "passed_ts",
              "created_ts")
    raw_id_fields = ("text_pair", )
    readonly_fields = ("passed_ts", "created_ts",)


#     question = models.TextField(max_length=2048, blank=False)
    # possible_answers = models.TextField(max_length=2048, blank=False)
    # answer = models.TextField(max_length=2048, blank=True)
