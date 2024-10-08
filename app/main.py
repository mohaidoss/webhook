from fastapi import FastAPI
from api.webhook_controller import router as webhook_router

app = FastAPI(
    docs_url=None,
    redoc_url=None,
)


app.include_router(webhook_router)
