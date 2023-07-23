from pprint import pprint
import re
from django.core.management.base import BaseCommand
from slfrase.models import TextPair
from django.db import models
from django.db.models.functions import Lower
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Load text pairs"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("files", nargs="+")

    def handle(self, *args, **options):
        print(options["files"])
        for filename in options["files"]:
            with open(filename, 'r', encoding='utf-8') as f:
                pairs = f.readlines()
            pairs = [s.lower().strip() for s in pairs]
            pairs = [s for s in pairs if len(s) > 0]
            pairs = [s for s in pairs if s and not s.startswith('#')]
            pairs = [re.split('\s+-\s+', s) for s in pairs]
            pprint([s for s in pairs if len(s) != 2])
            pairs = [[s1.strip(), s2.strip()] for s1, s2 in pairs]
            pairs = [[re.split('\s*,\s*', s1), re.split('\s*,\s*', s2)]
                     for s1, s2 in pairs]
            pairs = [['\n'.join(s1), '\n'.join(s2)] for s1, s2 in pairs]

            User = get_user_model()
            user = User.objects.filter(username="a").get()
            for text1, text2 in pairs:
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
                f'All pairs from "{filename}" was loaded successfully'
            ))
