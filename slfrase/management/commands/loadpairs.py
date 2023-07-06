import re
from django.core.management.base import BaseCommand
from slfrase.models import TextPair
from django.db import models
from django.db.models.functions import Lower
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Load text pairs"

    def handle(self, *args, **options):
        with open('es-ru.txt', 'r', encoding='utf-8') as f:
            newWords = f.readlines()
        newWords = [s.lower().strip() for s in newWords]
        newWords = [s for s in newWords if s and not s.startswith('#')]
        newWords = [re.split('\s*-\s*', s) for s in newWords]
        newWords = [[s1.strip(), s2.strip()] for s1,s2 in newWords]
        newWords = [[re.split('\s*,\s*', s1), re.split('\s*,\s*', s2)] for s1,s2 in newWords]
        newWords = [['\n'.join(s1), '\n'.join(s2)] for s1,s2 in newWords]

        User = get_user_model()
        user = User.objects.filter(username="a").get()
        for text1, text2 in newWords:
            p = TextPair.objects.annotate(
                text1_lower=Lower('text1'),
                text2_lower=Lower('text2'),
            ).filter(
                models.Q(user=user),
                models.Q(
                    text1_lower=Lower(models.Value(text1))
                ) | models.Q(
                    text2_lower=Lower(models.Value(text2))
                ),
            ).first()
            if p:
                if p.text1 != text1 or p.text2 != text2:
                    p.text1 = text1
                    p.text2 = text2
                    p.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'\tUpdated {p.pk}: "{text1[:10]}...", "{text2[:10]}..."'
                    ))
            else:
                p = TextPair.objects.create(
                    user=user,
                    text1=text1,
                    text2=text2,
                )
                self.stdout.write(self.style.SUCCESS(
                    f'\tCreated {p.pk}: "{text1[:10]}...", "{text2[:10]}..."'
                ))
        self.stdout.write(self.style.SUCCESS(
            'Successfully loaded all pairs'
        ))
