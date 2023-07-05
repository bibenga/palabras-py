from django.core.management.base import BaseCommand
from slfrase.models import TextPair
from django.db import models
from django.db.models.functions import Lower
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Load text pairs"

# (.+)	(.+)
# ("$1", "$2"),
    data = [
        ("decir", "сказать\nговорить"),
        ("empezar\ncomenzar", "начать\nначинать"),
        ("dar", "давать"),
        ("volver", "возвращаться"),
        ("abrir", "открывать"),
        ("cerrar", "закрыть"),
        ("contar", "считать"),
        ("encontrar", "находить"),
        ("contestar", "отвечать"),
        ("Nadie", "Ни кто"),
        ("Nada", "Ни что\nНичего"),
    ]

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.filter(username="a").get()
        for text1, text2 in self.data:
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
