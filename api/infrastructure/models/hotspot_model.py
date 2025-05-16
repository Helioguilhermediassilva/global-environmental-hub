"""SQLAlchemy model for hotspots."""
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Float, Integer, String

from api.infrastructure.models.base import Base


class HotspotModel(Base):
    """SQLAlchemy model for hotspots."""

    __tablename__ = "hotspots"

    id = Column(String, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geom = Column(Geometry(geometry_type="POINT", srid=4326))
    acquisition_date = Column(DateTime, nullable=False)
    confidence = Column(Integer, nullable=False)
    source = Column(String, nullable=False)
    brightness = Column(Float)
    frp = Column(Float)
    biome = Column(String)
    land_use = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
