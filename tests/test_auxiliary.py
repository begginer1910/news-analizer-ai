import pytest
from auxiliary_functions import Auxiliary


@pytest.mark.parametrize("input_language, expected",[
    ("english", "en"),
    ("English", "en"),
    (" english " , "en"),
    ("en", "en"),
    ("japanese", None),
    ("", None),
])


def test_validate_language(input_language: str, expected):
    a = Auxiliary()
    result = a.validate_language(input_language)
    assert result == expected


@pytest.mark.parametrize("input_category, expected",[
    ("general", "general"),
    ("General", "general"),
    (" general ", "general"),
    ("economy" , None),
    ("", None),
])


def test_validate_category(input_category: str, expected):
    a = Auxiliary()
    result = a.validate_category(input_category)
    assert result == expected


@pytest.mark.parametrize("input_country, expected",[
    ("united states", "us"),
    ("United States", "us"),
    (" united states ", "us"),
    ("us", "us"),
    ("estonia", None),
    ("", None),
])


def test_validate_country(input_country: str, expected):
    a = Auxiliary()
    result = a.validate_country(input_country)
    assert result == expected


@pytest.mark.parametrize("mock_input, expected",[
    ("text", "text"),
    ("Text", "text"),
    (" text ", "text"),
])


def test_validate_text(monkeypatch, mock_input, expected):
    monkeypatch.setattr("builtins.input", lambda _: mock_input)
    a = Auxiliary()
    result = a.text("input: ")
    assert result == expected

@pytest.mark.parametrize("mock_input, expected",[
    ("42", 42),
    ("-2", -2),
    ("0", 0),
    (" 10 ", 10),
])


def test_validate_number(monkeypatch, mock_input, expected):
    monkeypatch.setattr("builtins.input", lambda _: mock_input)
    a = Auxiliary()
    result = a.numbers("input: ")
    assert result == expected


def test_numbers_invalid_valid(monkeypatch):
    inputs = iter(["abcd", "", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    a = Auxiliary()
    result = a.numbers("input: ")
    assert result == 3