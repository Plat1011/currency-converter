import httpx
import pytest
import respx

from currency_converter.infrastructure.exceptions import (
    ExternalServiceBadRequest,
    ExternalServiceUnavailable,
)
from currency_converter.infrastructure.frankfurter_client import FrankfurterClient


@pytest.mark.asyncio
async def test_get_currencies_success():
    client = FrankfurterClient()

    with respx.mock:
        respx.get("https://api.frankfurter.app/currencies").respond(
            200, json={"USD": "United States Dollar", "EUR": "Euro"}
        )

        result = await client.get_currencies()
        assert result["USD"] == "United States Dollar"
        assert result["EUR"] == "Euro"


@pytest.mark.asyncio
async def test_get_currencies_invalid_format():
    client = FrankfurterClient()

    with respx.mock:
        respx.get("https://api.frankfurter.app/currencies").respond(200, json=[1, 2, 3])

        with pytest.raises(ExternalServiceUnavailable):
            await client.get_currencies()


@pytest.mark.asyncio
async def test_get_rate_success():
    client = FrankfurterClient()

    with respx.mock:
        route = respx.get("https://api.frankfurter.app/latest")
        route.respond(
            200,
            json={"amount": 1.0, "base": "USD", "date": "2024-01-01", "rates": {"EUR": 0.9}},
        )

        rate = await client.get_rate("USD", "EUR")
        assert rate == 0.9

        request = route.calls[0].request
        assert request.url.params["from"] == "USD"
        assert request.url.params["to"] == "EUR"


@pytest.mark.asyncio
async def test_get_rate_missing_target_currency():
    client = FrankfurterClient()

    with respx.mock:
        respx.get("https://api.frankfurter.app/latest").respond(
            200,
            json={"amount": 1.0, "base": "USD", "date": "2024-01-01", "rates": {"GBP": 0.8}},
        )

        with pytest.raises(ExternalServiceBadRequest):
            await client.get_rate("USD", "EUR")


@pytest.mark.asyncio
async def test_get_rate_invalid_rate_type():
    client = FrankfurterClient()

    with respx.mock:
        respx.get("https://api.frankfurter.app/latest").respond(
            200,
            json={"amount": 1.0, "base": "USD", "date": "2024-01-01", "rates": {"EUR": "0.9"}},
        )

        with pytest.raises(ExternalServiceUnavailable):
            await client.get_rate("USD", "EUR")


@pytest.mark.asyncio
async def test_get_rate_4xx_becomes_bad_request():
    client = FrankfurterClient()

    with respx.mock:
        respx.get("https://api.frankfurter.app/latest").respond(400, json={"message": "bad request"})

        with pytest.raises(ExternalServiceBadRequest):
            await client.get_rate("XXX", "EUR")


@pytest.mark.asyncio
async def test_get_rate_5xx_becomes_unavailable():
    client = FrankfurterClient(max_retries=0)

    with respx.mock:
        respx.get("https://api.frankfurter.app/latest").respond(503, json={"message": "down"})

        with pytest.raises(ExternalServiceUnavailable):
            await client.get_rate("USD", "EUR")


@pytest.mark.asyncio
async def test_get_json_timeout_retried_then_unavailable():
    client = FrankfurterClient(max_retries=2)

    with respx.mock:
        respx.get("https://api.frankfurter.app/latest").mock(
            side_effect=httpx.TimeoutException("timeout")
        )

        with pytest.raises(ExternalServiceUnavailable):
            await client.get_rate("USD", "EUR")


@pytest.mark.asyncio
async def test_get_json_network_error_retried_then_unavailable():
    client = FrankfurterClient(max_retries=1)

    with respx.mock:
        respx.get("https://api.frankfurter.app/latest").mock(
            side_effect=httpx.NetworkError("network")
        )

        with pytest.raises(ExternalServiceUnavailable):
            await client.get_rate("USD", "EUR")


@pytest.mark.asyncio
async def test_get_json_invalid_json_becomes_unavailable():
    client = FrankfurterClient(max_retries=2)

    with respx.mock:
        respx.get("https://api.frankfurter.app/latest").respond(200, content=b"not-json")

        with pytest.raises(ExternalServiceUnavailable):
            await client.get_rate("USD", "EUR")
