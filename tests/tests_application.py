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






@pytest.mark.asyncio
async def test_usecase_same_currency():
    class BombRatesProvider:
        async def get_rate(self, from_currency: str, to_currency: str) -> float:
            raise RuntimeError("Should not be called")

    uc = ConvertCurrencyUseCase(rates=BombRatesProvider())

    res = await uc.execute(
        ConvertCurrencyCommand(amount=10, from_code="USD", to_code="USD")
    )

    assert res.rate == 1.0
    assert res.result.amount == 10
    assert res.result.currency.code == "USD"


@pytest.mark.asyncio
async def test_usecase_external_bad_request():
    class BadProvider:
        async def get_rate(self, from_currency: str, to_currency: str) -> float:
            raise ExternalServiceBadRequest("Rate not found")

    uc = ConvertCurrencyUseCase(rates=BadProvider())

    with pytest.raises(ConversionBadRequest):
        await uc.execute(ConvertCurrencyCommand(amount=10, from_code="USD", to_code="ZZZ"))


@pytest.mark.asyncio
async def test_usecase_external_unavailable():
    class UnavailableProvider:
        async def get_rate(self, from_currency: str, to_currency: str) -> float:
            raise ExternalServiceUnavailable("Timeout")

    uc = ConvertCurrencyUseCase(rates=UnavailableProvider())

    with pytest.raises(ConversionUnavailable):
        await uc.execute(ConvertCurrencyCommand(amount=10, from_code="USD", to_code="EUR"))
