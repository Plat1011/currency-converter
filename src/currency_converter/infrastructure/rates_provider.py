from __future__ import annotations

from currency_converter.application.exceptions import (
    RatesProviderBadRequest,
    RatesProviderUnavailable,
)
from currency_converter.application.ports import RatesProvider
from currency_converter.infrastructure.exceptions import (
    ExternalServiceBadRequest,
    ExternalServiceUnavailable,
)
from currency_converter.infrastructure.frankfurter_client import FrankfurterClient


class FrankfurterRatesProvider(RatesProvider):
    def __init__(self, client: FrankfurterClient | None = None) -> None:
        self._client = client or FrankfurterClient()

    async def get_currencies(self) -> dict[str, str]:
        try:
            return await self._client.get_currencies()
        except ExternalServiceBadRequest as e:
            raise RatesProviderBadRequest(str(e)) from e
        except ExternalServiceUnavailable as e:
            raise RatesProviderUnavailable(str(e)) from e

    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        try:
            return await self._client.get_rate(from_currency, to_currency)
        except ExternalServiceBadRequest as e:
            raise RatesProviderBadRequest(str(e)) from e
        except ExternalServiceUnavailable as e:
            raise RatesProviderUnavailable(str(e)) from e

STATIC_CURRENCIES: dict[str, str] = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound Sterling",
    "JPY": "Japanese Yen",
    "RUB": "Russian Ruble",
    "KZT": "Kazakhstani Tenge",
}

STATIC_RATES: dict[str, dict[str, float]] = {
    "USD": {"EUR": 0.92, "GBP": 0.79, "JPY": 155.2, "RUB": 90.5, "KZT": 447.0},
    "EUR": {"USD": 1.09, "GBP": 0.86, "JPY": 168.4, "RUB": 98.3, "KZT": 486.8},
    "GBP": {"USD": 1.27, "EUR": 1.16, "JPY": 196.1, "RUB": 114.4, "KZT": 566.0},
    "JPY": {"USD": 0.0064, "EUR": 0.0059, "GBP": 0.0051, "RUB": 0.58, "KZT": 2.88},
    "RUB": {"USD": 0.011, "EUR": 0.010, "GBP": 0.0087, "JPY": 1.71, "KZT": 4.95},
    "KZT": {"USD": 0.0022, "EUR": 0.0021, "GBP": 0.0018, "JPY": 0.35, "RUB": 0.20},
}


class StaticRatesProvider(RatesProvider):
    def __init__(
        self,
        currencies: dict[str, str] | None = None,
        rates: dict[str, dict[str, float]] | None = None,
    ) -> None:
        self._currencies = currencies or STATIC_CURRENCIES
        self._rates = rates or STATIC_RATES

    async def get_currencies(self) -> dict[str, str]:
        return self._currencies

    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        if from_currency == to_currency:
            return 1.0

        from_rates = self._rates.get(from_currency)
        if not from_rates:
            raise RatesProviderBadRequest(f"Unknown source currency: {from_currency}")

        rate = from_rates.get(to_currency)
        if rate is None:
            raise RatesProviderBadRequest(
                f"Rate not found for {from_currency}->{to_currency}"
            )

        return rate