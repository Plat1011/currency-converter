from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict, Optional

import httpx

from .exceptions import ExternalServiceBadRequest, ExternalServiceUnavailable


@dataclass(frozen=True)
class FrankfurterClient:
    base_url: str = "https://api.frankfurter.app"
    timeout_seconds: float = 5.0
    max_retries: int = 2

    async def get_currencies(self) -> Dict[str, str]:
        url = f"{self.base_url}/currencies"
        data = await self._get_json(url)
        if not isinstance(data, dict):
            raise ExternalServiceUnavailable("Invalid response format")
        return {str(k): str(v) for k, v in data.items()}

    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        url = f"{self.base_url}/latest"
        params = {"from": from_currency, "to": to_currency}

        data = await self._get_json(url, params=params)

        rates = data.get("rates") if isinstance(data, dict) else None
        if not isinstance(rates, dict) or to_currency not in rates:
            raise ExternalServiceBadRequest(
                f"Rate not found for {from_currency}->{to_currency}"
            )

        rate = rates[to_currency]
        if not isinstance(rate, (int, float)):
            raise ExternalServiceUnavailable("Invalid rate type")

        return float(rate)

    async def _get_json(self, url: str, params: Optional[dict] = None) -> dict:
        timeout = httpx.Timeout(self.timeout_seconds)
        last_exc: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.get(url, params=params)

                if 400 <= resp.status_code < 500:
                    raise ExternalServiceBadRequest(
                        f"External API rejected request: {resp.status_code}"
                    )

                if resp.status_code >= 500:
                    raise ExternalServiceUnavailable(
                        f"External API error: {resp.status_code}"
                    )

                return resp.json()

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_exc = e
            except ValueError as e:
                raise ExternalServiceUnavailable("Invalid JSON") from e
            except ExternalServiceBadRequest:
                raise
            except ExternalServiceUnavailable as e:
                last_exc = e

            if attempt < self.max_retries:
                await asyncio.sleep(0.2 * (attempt + 1))

        raise ExternalServiceUnavailable("External service unavailable") from last_exc
