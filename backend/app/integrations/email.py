"""Email provider abstraction."""

from abc import ABC, abstractmethod
from typing import Optional


class EmailProvider(ABC):
    """Abstract email provider interface."""

    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str, html: bool = False) -> dict:
        ...


class MockEmailProvider(EmailProvider):
    """Mock email provider for demo mode."""

    async def send_email(self, to, subject, body, html=False):
        return {"status": "mock_sent", "to": to, "subject": subject}


class ResendEmailProvider(EmailProvider):
    """Resend email provider (requires configuration)."""

    def __init__(self, api_key: str, from_email: str):
        self.api_key = api_key
        self.from_email = from_email

    async def send_email(self, to, subject, body, html=False):
        raise NotImplementedError("Resend email requires API key configuration")
