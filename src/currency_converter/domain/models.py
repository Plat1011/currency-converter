from dataclasses import dataclass


@dataclass(frozen=True)
class Currency:
    code: str


@dataclass(frozen=True)
class Money:
    amount: float
    currency: Currency
