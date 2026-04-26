from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from currency_converter.application.ports import RatesProvider
from currency_converter.application.use_cases import (
    ConvertCurrencyCommand,
    ConvertCurrencyUseCase,
    ConversionBadRequest,
    ConversionUnavailable,
)
from currency_converter.presentation.dependencies import get_rates_provider
from currency_converter.presentation.schemas import (
    ConvertRequest,
    ConvertResponse,
    CurrenciesResponse,
)
from currency_converter.presentation.receipt_pdf import build_receipt_pdf

router = APIRouter()


@router.get("/currencies", response_model=CurrenciesResponse)
async def get_currencies(rates: RatesProvider = Depends(get_rates_provider)):
    try:
        currencies = await rates.get_currencies()
        return {"currencies": currencies}
    except Exception as e:
        raise HTTPException(status_code=503, detail="External service unavailable") from e


@router.post("/convert", response_model=ConvertResponse)
async def convert_currency(
    payload: ConvertRequest,
    rates: RatesProvider = Depends(get_rates_provider),
):
    uc = ConvertCurrencyUseCase(rates=rates)

    try:
        res = await uc.execute(
            ConvertCurrencyCommand(
                amount=payload.amount,
                from_code=payload.from_currency,
                to_code=payload.to_currency,
            )
        )
    except ConversionBadRequest as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ConversionUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    return {
        "amount": res.source.amount,
        "from_currency": res.source.currency.code,
        "to_currency": res.result.currency.code,
        "rate": res.rate,
        "result": res.result.amount,
    }


@router.post("/receipt")
async def generate_receipt(
    payload: ConvertRequest,
    rates: RatesProvider = Depends(get_rates_provider),
):
    uc = ConvertCurrencyUseCase(rates=rates)

    try:
        res = await uc.execute(
            ConvertCurrencyCommand(
                amount=payload.amount,
                from_code=payload.from_currency,
                to_code=payload.to_currency,
            )
        )
    except ConversionBadRequest as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ConversionUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    pdf_bytes = build_receipt_pdf(
        amount=res.source.amount,
        from_currency=res.source.currency.code,
        to_currency=res.result.currency.code,
        rate=res.rate,
        result=res.result.amount,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                "inline; filename=currency-converter-receipt.pdf"
            )
        },
    )

