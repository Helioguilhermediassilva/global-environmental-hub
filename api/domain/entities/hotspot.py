"""Hotspot entity representing a fire hotspot."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Hotspot(BaseModel):
    """Hotspot entity representing a fire hotspot detected by satellite."""

    id: Optional[str] = Field(None, description="Unique identifier for the hotspot")
    latitude: float = Field(..., description="Latitude of the hotspot")
    longitude: float = Field(..., description="Longitude of the hotspot")
    acquisition_date: datetime = Field(..., description="Date and time of acquisition")
    confidence: int = Field(..., description="Confidence level (0-100)")
    source: str = Field(..., description="Source of the data (e.g., MODIS, VIIRS)")
    brightness: Optional[float] = Field(None, description="Brightness temperature (Kelvin)")
    frp: Optional[float] = Field(None, description="Fire Radiative Power (MW)")
    biome: Optional[str] = Field(None, description="Biome where the hotspot was detected")
    land_use: Optional[str] = Field(None, description="Land use classification")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Record update timestamp")

    class Config:
        """Pydantic model configuration."""

        schema_extra = {
            "example": {
                "id": "FIRMS_123456",
                "latitude": -9.45678,
                "longitude": -56.78901,
                "acquisition_date": "2025-05-15T14:30:00",
                "confidence": 85,
                "source": "VIIRS",
                "brightness": 325.7,
                "frp": 45.2,
                "biome": "Amazon Rainforest",
                "land_use": "Forest",
                "created_at": "2025-05-15T15:00:00",
                "updated_at": "2025-05-15T15:00:00",
            }
        }
