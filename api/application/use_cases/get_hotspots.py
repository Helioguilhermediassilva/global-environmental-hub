"""Use case for retrieving hotspots."""
from datetime import datetime
from typing import List, Optional, Tuple

from api.domain.entities.hotspot import Hotspot


class GetHotspotsUseCase:
    """Use case for retrieving hotspots based on criteria."""

    def __init__(self, hotspot_repository):
        """Initialize use case with repository dependency.
        
        Args:
            hotspot_repository: Repository for hotspot data access
        """
        self.hotspot_repository = hotspot_repository

    async def execute(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_confidence: Optional[int] = None,
        source: Optional[str] = None,
        biome: Optional[str] = None,
        bounding_box: Optional[Tuple[float, float, float, float]] = None,
    ) -> List[Hotspot]:
        """Execute the use case to retrieve hotspots.
        
        Args:
            start_date: Start date for filtering hotspots
            end_date: End date for filtering hotspots
            min_confidence: Minimum confidence level
            source: Source of the data (e.g., MODIS, VIIRS)
            biome: Biome filter
            bounding_box: Geographical bounding box (min_lon, min_lat, max_lon, max_lat)
            
        Returns:
            List of hotspots matching the criteria
        """
        return await self.hotspot_repository.find_by_criteria(
            start_date=start_date,
            end_date=end_date,
            min_confidence=min_confidence,
            source=source,
            biome=biome,
            bounding_box=bounding_box,
        )
