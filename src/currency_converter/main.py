from fastapi import FastAPI

from currency_converter.presentation.api import router


def create_app() -> FastAPI:
    app = FastAPI(title="Currency Converter")
    app.include_router(router)
    return app


app = create_app()
