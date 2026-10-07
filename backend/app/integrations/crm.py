"""Generic CRM integration abstraction."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class CRMProvider(ABC):
    """Abstract CRM provider interface."""

    @abstractmethod
    async def create_contact(self, contact_data: dict) -> dict:
        ...

    @abstractmethod
    async def update_contact(self, contact_id: str, data: dict) -> dict:
        ...

    @abstractmethod
    async def create_note(self, contact_id: str, note: str) -> dict:
        ...

    @abstractmethod
    async def add_tag(self, contact_id: str, tag: str) -> dict:
        ...


class MockCRMProvider(CRMProvider):
    """Mock CRM provider for demo mode."""

    def __init__(self):
        self._contacts: dict[str, dict] = {}
        self._counter = 0

    async def create_contact(self, contact_data):
        self._counter += 1
        cid = f"mock_contact_{self._counter}"
        self._contacts[cid] = {"id": cid, **contact_data}
        return self._contacts[cid]

    async def update_contact(self, contact_id, data):
        contact = self._contacts.get(contact_id, {"id": contact_id})
        contact.update(data)
        return contact

    async def create_note(self, contact_id, note):
        return {"contact_id": contact_id, "note": note}

    async def add_tag(self, contact_id, tag):
        return {"contact_id": contact_id, "tag": tag}
