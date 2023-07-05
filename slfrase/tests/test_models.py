import pytest
from slid.models import User
from slfrase.models import TextPair


@pytest.fixture
def user() -> User:
    return User.objects.create(username="a")


@pytest.fixture
def text_pair1(user) -> TextPair:
    return TextPair.objects.create(
        user=user,
        text1="Hola",
        text2="Привет",
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("text_pair1")
def test_hz() -> None:
    assert TextPair.objects.count() == 1
    p1 = TextPair.objects.get()
    assert p1 is not None
    assert p1.text1 == "Hola"


def test_get_text_list() -> None:
    text = " Uno \n Dos, Mas "
    text_list = ("Uno", "Dos, Mas")
    assert TextPair.get_text_list(text) == text_list

def test_get_words() -> None:
    frase = "Uño Dos, Más"
    words = ("Uno", "Dos", "Mas")
    assert TextPair.get_words(frase) == words
