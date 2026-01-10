import pytest

from currency_converter.application.use_cases import (
    ConvertCurrencyCommand,
    ConvertCurrencyUseCase,
    ConversionBadRequest,
    ConversionUnavailable,
)

from currency_converter.infrastructure.exceptions import (
    ExternalServiceBadRequest,
    ExternalServiceUnavailable,
)


class FakeRatesProvider:
    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        return 2.0


@pytest.mark.asyncio
async def test_usecase_converts_using_rate_provider():
    uc = ConvertCurrencyUseCase(rates=FakeRatesProvider())

    res = await uc.execute(
        ConvertCurrencyCommand(amount=10, from_code="usd", to_code="eur")
    )

    assert res.rate == 2.0
    assert res.source.amount == 10
    assert res.source.currency.code == "USD"
    assert res.result.currency.code == "EUR"
    assert res.result.amount == 20


@pytest.mark.asyncio
async def test_usecase_same_currency_skips_rate_provider():
    class BombRatesProvider:
        async def get_rate(self, from_currency: str, to_currency: str) -> float:
            raise RuntimeError("Should not be called")

    uc = ConvertCurrencyUseCase(rates=BombRatesProvider())

    res = await uc.execute(
        ConvertCurrencyCommand(amount=10, from_code="usd", to_code="usd")
    )

    assert res.rate == 1.0
    assert res.result.amount == 10
    assert res.result.currency.code == "USD"


@pytest.mark.asyncio
async def test_usecase_maps_external_bad_request_to_application_error():
    class BadProvider:
        async def get_rate(self, from_currency: str, to_currency: str) -> float:
            raise ExternalServiceBadRequest("Rate not found")

    uc = ConvertCurrencyUseCase(rates=BadProvider())

    with pytest.raises(ConversionBadRequest):
        await uc.execute(ConvertCurrencyCommand(amount=10, from_code="USD", to_code="ZZZ"))


@pytest.mark.asyncio
async def test_usecase_maps_external_unavailable_to_application_error():
    class UnavailableProvider:
        async def get_rate(self, from_currency: str, to_currency: str) -> float:
            raise ExternalServiceUnavailable("Timeout")

    uc = ConvertCurrencyUseCase(rates=UnavailableProvider())

    with pytest.raises(ConversionUnavailable):
        await uc.execute(ConvertCurrencyCommand(amount=10, from_code="USD", to_code="EUR"))
