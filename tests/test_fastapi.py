from fastapi.testclient import TestClient

from currency_converter.main import create_app
from currency_converter.presentation.dependencies import get_rates_provider
from currency_converter.application.use_cases import ConversionBadRequest, ConversionUnavailable


class Provider:
    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        return 0.5

    async def get_currencies(self) -> dict[str, str]:
        return {"USD": "US Dollar", "EUR": "Euro"}


class BadRequestProvider:
    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        raise ConversionBadRequest("Rate not found")

    async def get_currencies(self) -> dict[str, str]:
        return {"USD": "US Dollar"}


class UnavailableProvider:
    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        raise ConversionUnavailable("Timeout")

    async def get_currencies(self) -> dict[str, str]:
        raise ConversionUnavailable("Timeout")


def make_client(provider) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_rates_provider] = lambda: provider
    return TestClient(app)


def test_get_currencies():
    client = make_client(Provider())

    r = client.get("/currencies")
    assert r.status_code == 200
    body = r.json()
    assert "currencies" in body
    assert body["currencies"]["USD"] == "US Dollar"


def test_convert():
    client = make_client(Provider())

    r = client.post(
        "/convert",
        json={"amount": 10, "from_currency": "USD", "to_currency": "EUR"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["amount"] == 10
    assert body["from_currency"] == "USD"
    assert body["to_currency"] == "EUR"
    assert body["rate"] == 0.5
    assert body["result"] == 5.0


def test_convert_error():
    client = make_client(Provider())

    r = client.post(
        "/convert",
        json={"amount": 0, "from_currency": "USD", "to_currency": "EUR"},
    )
    assert r.status_code == 422


def test_convert_400():
    client = make_client(BadRequestProvider())

    r = client.post(
        "/convert",
        json={"amount": 10, "from_currency": "USD", "to_currency": "ZZZ"},
    )
    assert r.status_code == 400


def test_currencies_503():
    client = make_client(UnavailableProvider())

    r = client.get("/currencies")
    assert r.status_code == 503
