from __future__ import annotations
from typing import Protocol


class RatesProvider(Protocol):
    async def get_rate(self, from_currency: str, to_currency: str) -> float: ...
