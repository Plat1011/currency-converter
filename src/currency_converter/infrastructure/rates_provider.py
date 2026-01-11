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