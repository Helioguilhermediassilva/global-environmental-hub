"""Controller for hotspot endpoints."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from api.application.use_cases.get_hotspots import GetHotspotsUseCase
from api.domain.entities.hotspot import Hotspot
from api.infrastructure.dependencies.database import get_db_session
from api.infrastructure.repositories.hotspot_repository import HotspotRepository

router = APIRouter(prefix="/hotspots", tags=["hotspots"])


@router.get("/", response_model=List[Hotspot])
async def get_hotspots(
    start_date: Optional[datetime] = Query(None, description="Data inicial para filtrar hotspots"),
    end_date: Optional[datetime] = Query(None, description="Data final para filtrar hotspots"),
    min_confidence: Optional[int] = Query(None, description="Nível mínimo de confiança"),
    source: Optional[str] = Query(None, description="Fonte dos dados (ex: MODIS, VIIRS)"),
    biome: Optional[str] = Query(None, description="Filtro por bioma"),
    min_lon: Optional[float] = Query(None, description="Longitude mínima para bounding box"),
    min_lat: Optional[float] = Query(None, description="Latitude mínima para bounding box"),
    max_lon: Optional[float] = Query(None, description="Longitude máxima para bounding box"),
    max_lat: Optional[float] = Query(None, description="Latitude máxima para bounding box"),
    session=Depends(get_db_session),
):
    """Obter hotspots com base em critérios."""
    # Criar bounding box se as coordenadas forem fornecidas
    bounding_box = None
    if all(coord is not None for coord in [min_lon, min_lat, max_lon, max_lat]):
        bounding_box = (min_lon, min_lat, max_lon, max_lat)

    # Criar repositório
    repository = HotspotRepository(session)
    
    # Criar e executar caso de uso
    use_case = GetHotspotsUseCase(repository)
    hotspots = await use_case.execute(
        start_date=start_date,
        end_date=end_date,
        min_confidence=min_confidence,
        source=source,
        biome=biome,
        bounding_box=bounding_box,
    )
    
    return hotspots
