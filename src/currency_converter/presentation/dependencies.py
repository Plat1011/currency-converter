from currency_converter.application.ports import RatesProvider
from currency_converter.infrastructure.rates_provider import FrankfurterRatesProvider


def get_rates_provider() -> RatesProvider:
    return FrankfurterRatesProvider()
