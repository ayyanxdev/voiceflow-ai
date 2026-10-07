"""Google Sheets integration abstraction."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class SheetsProvider(ABC):
    """Abstract Google Sheets provider."""

    @abstractmethod
    async def import_leads(self, spreadsheet_id: str, sheet_name: str = "Sheet1") -> list[dict]:
        ...

    @abstractmethod
    async def export_leads(self, spreadsheet_id: str, leads: list[dict], sheet_name: str = "Sheet1") -> bool:
        ...

    @abstractmethod
    async def append_call_result(self, spreadsheet_id: str, call_data: dict, sheet_name: str = "Calls") -> bool:
        ...


class MockSheetsProvider(SheetsProvider):
    """Mock sheets provider for demo mode."""

    async def import_leads(self, spreadsheet_id, sheet_name="Sheet1"):
        return []

    async def export_leads(self, spreadsheet_id, leads, sheet_name="Sheet1"):
        return True

    async def append_call_result(self, spreadsheet_id, call_data, sheet_name="Calls"):
        return True
