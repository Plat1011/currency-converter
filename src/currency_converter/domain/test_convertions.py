from models import Currency, Money
from services import convert


def test_convert_simple():
    result = convert(Money(10, Currency("USD")), Currency("EUR"), rate=0.9)
    assert result.amount == 9.0
    assert result.currency.code == "EUR"


def test_convert_same_currency():
    result = convert(Money(10, Currency("USD")), Currency("USD"), rate=123)
    assert result.amount == 10
