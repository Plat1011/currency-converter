from .models import Currency, Money


def convert(money: Money, to_currency: Currency, rate: float) -> Money:
    if money.currency.code == to_currency.code:
        return Money(amount=money.amount, currency=to_currency)

    return Money(amount=money.amount * rate, currency=to_currency)
