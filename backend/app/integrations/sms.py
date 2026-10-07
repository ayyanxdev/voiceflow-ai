"""SMS provider abstraction."""

from abc import ABC, abstractmethod
from typing import Optional


class SMSProvider(ABC):
    """Abstract SMS provider interface."""

    @abstractmethod
    async def send_sms(self, to: str, message: str, from_number: Optional[str] = None) -> dict:
        ...


class MockSMSProvider(SMSProvider):
    """Mock SMS provider for demo mode."""

    async def send_sms(self, to, message, from_number=None):
        return {"status": "mock_sent", "to": to, "message": message}


class TwilioSMSProvider(SMSProvider):
    """Twilio SMS provider (requires configuration)."""

    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number

    async def send_sms(self, to, message, from_number=None):
        raise NotImplementedError("Twilio SMS requires account configuration")
