from abc import ABC, abstractmethod
import json

from fastapi import HTTPException

from services.signature_verification_service import SignatureVerificationService
from ports import MessageSender

class WebhookHandler(ABC):

    def __init__(self, senders: list[MessageSender], signature_service: SignatureVerificationService):
        self.senders = senders
        self.signature_service = signature_service

    @abstractmethod
    async def process_webhook(self, payload: dict, headers: dict):
        pass


class ResendWebhookHandler(WebhookHandler):

    async def process_webhook(self, payload: bytes, headers: dict):
        if not self.signature_service.verify(payload, headers):
            raise HTTPException(status_code=401, detail="Invalid signature for Resend webhook.")

        payload = json.loads(payload)
        message = payload.get("data", "No data provided")
        event_type = payload.get("type", "Unknown event")
        formatted_message = f"""**Resend Event Received**
        **Type:** {event_type}
        **Details:** ```{json.dumps(message,indent=2)}```
        """

        for sender in self.senders:
            await sender.send_message(formatted_message)

class PrefectWebhookHandler(WebhookHandler):

    async def process_webhook(self, payload: dict, headers: dict):
        if not self.signature_service.verify_signature(payload, headers):
            raise HTTPException(status_code=401, detail="Invalid signature for Prefect webhook.")

        state_message = payload.get("state", {}).get("message", "No state message provided")
        formatted_message = f"Prefect Event: {state_message}"

        for sender in self.senders:
            await sender.send_message(formatted_message)
