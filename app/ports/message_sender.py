from abc import ABC, abstractmethod


class MessageSender(ABC):
    @abstractmethod
    async def send_message(self, message: str):
        pass
