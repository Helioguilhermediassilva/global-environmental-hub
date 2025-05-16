"""Base connector interface for data sources."""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseConnector(ABC):
    """Interface base for all data source connectors."""

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection with the data source."""
        pass

    @abstractmethod
    async def fetch_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from the source based on provided parameters."""
        pass

    @abstractmethod
    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data obtained from the source."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Return metadata about the data source."""
        pass
