from __future__ import annotations
from dataclasses import dataclass

from .ports import RatesProvider

from currency_converter.domain.models import Currency, Money
from currency_converter.domain.services import convert

from currency_converter.application.exceptions import (
    RatesProviderBadRequest,
    RatesProviderUnavailable,
)


class ConversionUnavailable(Exception):
    pass

class ConversionBadRequest(Exception):
    pass

@dataclass(frozen=True)
class ConvertCurrencyCommand:
    amount: float
    from_code: str
    to_code: str

@dataclass(frozen=True)
class ConvertCurrencyResult:
    source: Money
    result: Money
    rate: float


class ConvertCurrencyUseCase:
    def __init__(self, rates: RatesProvider) -> None:
        self._rates = rates

    async def execute(self, ccc: ConvertCurrencyCommand) -> ConvertCurrencyResult:
        from_code = ccc.from_code
        to_code = ccc.to_code

        from_currency = Currency(code=from_code)
        to_currency = Currency(code=to_code)
        money = Money(amount=ccc.amount, currency=from_currency)

        if from_code == to_code:
            rate = 1.0
            return ConvertCurrencyResult(
                source=money,
                result=convert(money=money, to_currency=to_currency, rate=rate),
                rate=rate,
            )

        try:
            rate = await self._rates.get_rate(from_code, to_code)
        except RatesProviderBadRequest as e:
            raise ConversionBadRequest(str(e)) from e
        except RatesProviderUnavailable as e:
            raise ConversionUnavailable(str(e)) from e

        result = convert(money=money, to_currency=to_currency, rate=rate)
        return ConvertCurrencyResult(source=money, result=result, rate=rate)
