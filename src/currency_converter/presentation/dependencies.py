from currency_converter.application.ports import RatesProvider
from currency_converter import config
from currency_converter.infrastructure.rates_provider import (
    FrankfurterRatesProvider,
    StaticRatesProvider,
)

def get_rates_provider() -> RatesProvider:
    if config.RATES_SOURCE == "api":
        return FrankfurterRatesProvider()
    return StaticRatesProvider()