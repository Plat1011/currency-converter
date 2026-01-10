from currency_converter.application.ports import RatesProvider
from currency_converter.infrastructure.frankfurter_client import FrankfurterClient


def get_rates_provider() -> RatesProvider:
    return FrankfurterClient()
