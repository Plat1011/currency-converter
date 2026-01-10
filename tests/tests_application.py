import pytest

from currency_converter.application.use_cases import ConvertCurrencyUseCase
from currency_converter.infrastructure.exceptions import (
    ExternalServiceBadRequest,
    ExternalServiceUnavailable,
)


class FakeRatesProvider:
    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        return 2.0

    async def get_currencies(self) -> dict[str, str]:
        return {"USD": "US Dollar", "EUR": "Euro"}


@pytest.mark.asyncio
async def test_usecase_converting():
    uc = ConvertCurrencyUseCase(rates_provider=FakeRatesProvider())

    res = await uc.execute(amount=10, from_code="USD", to_code="EUR")

    assert res["rate"] == 2.0
    assert res["amount"] == 10
    assert res["from_currency"] == "USD"
    assert res["to_currency"] == "EUR"
    assert res["result"] == 20.0


@pytest.mark.asyncio
async def test_usecase_external_bad_request_propagates():
    class BadProvider:
        async def get_rate(self, from_currency: str, to_currency: str) -> float:
            raise ExternalServiceBadRequest("Rate not found")

        async def get_currencies(self) -> dict[str, str]:
            return {}

    uc = ConvertCurrencyUseCase(rates_provider=BadProvider())

    with pytest.raises(ExternalServiceBadRequest):
        await uc.execute(amount=10, from_code="USD", to_code="ZZZ")


@pytest.mark.asyncio
async def test_usecase_external_unavailable_propagates():
    class UnavailableProvider:
        async def get_rate(self, from_currency: str, to_currency: str) -> float:
            raise ExternalServiceUnavailable("Timeout")

        async def get_currencies(self) -> dict[str, str]:
            return {}

    uc = ConvertCurrencyUseCase(rates_provider=UnavailableProvider())

    with pytest.raises(ExternalServiceUnavailable):
        await uc.execute(amount=10, from_code="USD", to_code="EUR")
