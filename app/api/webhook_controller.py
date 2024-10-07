import os
from typing import Annotated

from adapters.discord_sender import DiscordSender
from adapters.telegram_sender import TelegramSender
from fastapi import APIRouter, Header, HTTPException, Request
from models import PrefectEvent
from models.verification_header import VerificationHeader
from services.signature_verification_service import SignatureVerificationService
from services.webhook_service import PrefectWebhookHandler, ResendWebhookHandler

from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/v1")


DISCORD_WEBHOOKS_RESEND = os.getenv('DISCORD_ALERTS_WEBHOOK')


DISCORD_WEBHOOKS_PREFECT = os.getenv('DISCORD_ALERTS_WEBHOOK')


TELEGRAM_BOT_TOKEN = "XXXXX"
TELEGRAM_CHAT_ID = "123456"

resend_discord_sender = DiscordSender(DISCORD_WEBHOOKS_RESEND)
prefect_discord_sender = DiscordSender(DISCORD_WEBHOOKS_PREFECT)
telegram_sender = TelegramSender(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

RESEND_SIGN_SECRET = os.getenv('RESEND_SIGN_SECRET')
PREFECT_SIGN_SECRET = os.getenv('PREFECT_SIGN_SECRET')

resend_signature_service = SignatureVerificationService(RESEND_SIGN_SECRET)
prefect_signature_service = SignatureVerificationService(PREFECT_SIGN_SECRET)

resend_handler = ResendWebhookHandler([resend_discord_sender], resend_signature_service)
prefect_handler = PrefectWebhookHandler([prefect_discord_sender, telegram_sender], prefect_signature_service)

@router.post("/receive/resend")
async def resend_webhook(request: Request):
    headers = request.headers
    payload = await request.body()
    if not headers:
        raise HTTPException(status_code=400, detail="Missing Resend headers.")
    await resend_handler.process_webhook(payload, headers)
    return {"status": "success"}

@router.post("/receive/prefect")
async def prefect_webhook(headers: Annotated[VerificationHeader, Header()], request: PrefectEvent):
    print(headers)
    print(request)
    if not headers:
        raise HTTPException(status_code=400, detail="Missing Prefect headers.")

    await prefect_handler.process_webhook(request.model_dump(), headers.model_dump())
    return {"status": "success"}
