import re
from django.utils import timezone
from django.conf import settings
from django.db import models
import unidecode


class TextPair(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    text1 = models.TextField(max_length=2048, blank=False)
    text2 = models.TextField(max_length=2048, blank=False)
    comment = models.TextField(max_length=2048, blank=True)

    is_learned_flg = models.BooleanField(default=False)
    learned_ts = models.DateTimeField(null=True, blank=True)

    created_ts = models.DateTimeField(auto_now_add=True, editable=False)
    modified_ts = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created_ts',)

    def __str__(self):
        return self.text1[:100]

    def save(self, *args, **kwargs) -> None:
        if self.is_learned_flg:
            if not self.learned_ts:
                self.learned_ts = timezone.now()
        else:
            self.learned_ts = None
        return super().save(*args, **kwargs)

    @classmethod
    def get_text_list(cls, text: str) -> tuple[str, ...]:
        res = [x.strip() for x in text.splitlines()]
        return tuple(x for x in res if res)

    @classmethod
    def get_words(cls, text: str) -> tuple[str, ...]:
        res = (x.strip() for x in re.split("[ \r\n¡!¿?.,:;'\"]+", text))
        return tuple(unidecode.unidecode(x) for x in res if x)


class StudyState(models.Model):
    is_passed_flg = models.BooleanField(default=False)
    is_skipped_flg = models.BooleanField(default=False)
    passed_ts = models.DateTimeField(null=True, blank=True)

    text_pair = models.ForeignKey(TextPair, on_delete=models.CASCADE)
    question = models.TextField(max_length=2048, blank=False)
    possible_answers = models.TextField(max_length=2048, blank=False)
    answer = models.TextField(max_length=2048, blank=True)

    created_ts = models.DateTimeField(auto_now_add=True, editable=False)
    modified_ts = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created_ts',)

    def __str__(self):
        return str(self.text_pair)

    def save(self, *args, **kwargs) -> None:
        if self.is_passed_flg or self.is_skipped_flg:
            if not self.passed_ts:
                self.passed_ts = timezone.now()
        else:
            self.passed_ts = None
        return super().save(*args, **kwargs)
    
