from fastapi import HTTPException
import httpx
from ports import MessageSender


class DiscordSender(MessageSender):
    def __init__(self, webhook_url: str):
        """
        Initializes the DiscordSender with a webhook URL

        Args:
        - webhook_url (str): Discord webhook URL to send messages to.
        """
        self.webhook_url = webhook_url

    async def send_message(self, message: str):
        """
        Sends message to configured webhook
        """
        payload = {"content": message}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to send message to Discord webhook: {e}",
            )
