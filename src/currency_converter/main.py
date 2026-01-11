from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from currency_converter.config import CORS_ORIGINS
from currency_converter.presentation.api import router


def create_app() -> FastAPI:
    app = FastAPI(title="Currency Converter")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app


app = create_app()
