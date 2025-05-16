"""Connector for NASA FIRMS (Fire Information for Resource Management System)."""
import json
from typing import Any, Dict

import aiohttp

from data_ingestion.connectors.base_connector import BaseConnector


class NASAFirmsConnector(BaseConnector):
    """Connector for NASA FIRMS API."""

    def __init__(self, api_key: str, base_url: str = "https://firms.modaps.eosdis.nasa.gov/api/area"):
        """Initialize NASA FIRMS connector.

        Args:
            api_key: API key for NASA FIRMS
            base_url: Base URL for NASA FIRMS API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = None

    async def connect(self) -> bool:
        """Establish connection with NASA FIRMS API."""
        self.session = aiohttp.ClientSession()
        # Validate credentials and service availability
        try:
            params = {
                "key": self.api_key,
            }
            async with self.session.get(f"{self.base_url}/help", params=params) as response:
                return response.status == 200
        except Exception:
            return False

    async def fetch_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch hotspot data from NASA FIRMS API.

        Args:
            parameters: Query parameters for the API
                - area: Area of interest (country code, region, or coordinates)
                - date_range: Date range for data (YYYY-MM-DD/YYYY-MM-DD)
                - satellite: Satellite source (MODIS, VIIRS)
                - format: Output format (csv, geojson, shapefile)

        Returns:
            Dictionary containing the fetched data
        """
        if not self.session:
            await self.connect()

        # Add API key to parameters
        params = {
            "key": self.api_key,
            **parameters,
        }

        try:
            async with self.session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    return {"error": f"API returned status code {response.status}"}

                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    data = await response.json()
                    return {"data": data, "format": "json"}
                elif "text/csv" in content_type:
                    text = await response.text()
                    return {"data": text, "format": "csv"}
                else:
                    binary = await response.read()
                    return {"data": binary, "format": "binary"}
        except Exception as e:
            return {"error": str(e)}

    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data obtained from NASA FIRMS API."""
        if "error" in data:
            return False

        if data.get("format") == "json":
            # Check if data contains expected fields
            json_data = data.get("data", {})
            return isinstance(json_data, dict) and "features" in json_data
        elif data.get("format") == "csv":
            # Check if CSV data is not empty and has expected format
            csv_data = data.get("data", "")
            lines = csv_data.strip().split("\n")
            return len(lines) > 1 and "latitude" in lines[0].lower()
        else:
            # For binary data, just check if it's not empty
            return len(data.get("data", b"")) > 0

    def get_metadata(self) -> Dict[str, Any]:
        """Return metadata about NASA FIRMS data source."""
        return {
            "name": "NASA FIRMS",
            "description": "Fire Information for Resource Management System",
            "data_types": ["hotspots", "burned_areas"],
            "spatial_coverage": "global",
            "temporal_resolution": "daily",
            "formats": ["csv", "geojson", "shapefile"],
            "documentation_url": "https://firms.modaps.eosdis.nasa.gov/api/",
        }

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def __aenter__(self):
        """Enter async context."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        await self.close()
