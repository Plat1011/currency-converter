import importlib
import asyncio

import pytest

from currency_converter.application.exceptions import RatesProviderBadRequest
from currency_converter.infrastructure.rates_provider import StaticRatesProvider


def test_static_provider_get_currencies():
    provider = StaticRatesProvider()
    currencies = asyncio.run(provider.get_currencies())

    assert "USD" in currencies
    assert "EUR" in currencies


def test_static_provider_get_rate_success():
    provider = StaticRatesProvider()

    rate = asyncio.run(provider.get_rate("USD", "EUR"))

    assert rate > 0


def test_static_provider_get_rate_same_currency():
    provider = StaticRatesProvider()

    rate = asyncio.run(provider.get_rate("USD", "USD"))

    assert rate == 1.0


def test_static_provider_get_rate_unknown_currency():
    provider = StaticRatesProvider()

    with pytest.raises(RatesProviderBadRequest):
        asyncio.run(provider.get_rate("ZZZ", "USD"))


def test_dependencies_default_to_static(monkeypatch):
    monkeypatch.delenv("RATES_SOURCE", raising=False)

    import currency_converter.config as config
    import currency_converter.presentation.dependencies as dependencies

    importlib.reload(config)
    importlib.reload(dependencies)
    provider = dependencies.get_rates_provider()

    assert provider.__class__.__name__ == "StaticRatesProvider"


def test_dependencies_switch_to_api(monkeypatch):
    monkeypatch.setenv("RATES_SOURCE", "api")

    import currency_converter.config as config
    import currency_converter.presentation.dependencies as dependencies

    importlib.reload(config)
    importlib.reload(dependencies)
    provider = dependencies.get_rates_provider()

    assert provider.__class__.__name__ == "FrankfurterRatesProvider"