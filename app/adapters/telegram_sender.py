from fastapi import HTTPException
import httpx
from ports import MessageSender

TELEGRAM_API_URL = "https://api.telegram.org/bot{0}/sendMessage"


class TelegramSender(MessageSender):
    def __init__(self, token: str, chat_id):
        """
        Initializes the TelegramSender.

        Args:
        - token (str): TELEGRAM BOT TOKEN to send messages in his behalf.
        """
        self.token = token
        self.chat_id = chat_id

    async def send_message(self, message: str):
        """
        Sends message to configured webhook
        """
        payload = {"chat_id": self.chat_id, "text": message}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    TELEGRAM_API_URL.format(self.token), json=payload
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to send message to Discord webhook: {e}",
            )
