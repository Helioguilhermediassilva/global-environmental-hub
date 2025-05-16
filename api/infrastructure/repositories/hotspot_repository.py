"""Data access layer for hotspots."""
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.domain.entities.hotspot import Hotspot
from api.infrastructure.models.hotspot_model import HotspotModel


class HotspotRepository:
    """Repository for hotspot data access."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def find_by_criteria(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_confidence: Optional[int] = None,
        source: Optional[str] = None,
        biome: Optional[str] = None,
        bounding_box: Optional[Tuple[float, float, float, float]] = None,
    ) -> List[Hotspot]:
        """Find hotspots by criteria.
        
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
        # Build query
        query = select(HotspotModel)
        
        # Apply filters
        if start_date:
            query = query.where(HotspotModel.acquisition_date >= start_date)
        if end_date:
            query = query.where(HotspotModel.acquisition_date <= end_date)
        if min_confidence:
            query = query.where(HotspotModel.confidence >= min_confidence)
        if source:
            query = query.where(HotspotModel.source == source)
        if biome:
            query = query.where(HotspotModel.biome == biome)
        if bounding_box:
            min_lon, min_lat, max_lon, max_lat = bounding_box
            # This is a simplified example - in a real implementation,
            # you would use PostGIS functions for spatial queries
            query = query.where(HotspotModel.longitude >= min_lon)
            query = query.where(HotspotModel.longitude <= max_lon)
            query = query.where(HotspotModel.latitude >= min_lat)
            query = query.where(HotspotModel.latitude <= max_lat)
        
        # Execute query
        result = await self.session.execute(query)
        hotspot_models = result.scalars().all()
        
        # Convert models to domain entities
        return [
            Hotspot(
                id=model.id,
                latitude=model.latitude,
                longitude=model.longitude,
                acquisition_date=model.acquisition_date,
                confidence=model.confidence,
                source=model.source,
                brightness=model.brightness,
                frp=model.frp,
                biome=model.biome,
                land_use=model.land_use,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            for model in hotspot_models
        ]
        
    async def save(self, hotspot: Hotspot) -> Hotspot:
        """Save a hotspot to the database.
        
        Args:
            hotspot: Hotspot entity to save
            
        Returns:
            Saved hotspot with updated ID
        """
        # Create model from entity
        model = HotspotModel(
            id=hotspot.id,
            latitude=hotspot.latitude,
            longitude=hotspot.longitude,
            acquisition_date=hotspot.acquisition_date,
            confidence=hotspot.confidence,
            source=hotspot.source,
            brightness=hotspot.brightness,
            frp=hotspot.frp,
            biome=hotspot.biome,
            land_use=hotspot.land_use,
        )
        
        # Save model
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        
        # Return updated entity
        return Hotspot(
            id=model.id,
            latitude=model.latitude,
            longitude=model.longitude,
            acquisition_date=model.acquisition_date,
            confidence=model.confidence,
            source=model.source,
            brightness=model.brightness,
            frp=model.frp,
            biome=model.biome,
            land_use=model.land_use,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
