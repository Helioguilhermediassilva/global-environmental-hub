"""Testes para o endpoint de hotspots."""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.domain.entities.hotspot import Hotspot
from api.main import app


@pytest.fixture
def test_client():
    """Criar cliente de teste para a API."""
    return TestClient(app)


@pytest.fixture
def mock_hotspots():
    """Criar lista de hotspots simulados."""
    return [
        Hotspot(
            id="FIRMS_12345678",
            latitude=-9.45678,
            longitude=-56.78901,
            acquisition_date=datetime.now() - timedelta(days=1),
            confidence=85,
            source="VIIRS",
            brightness=325.7,
            frp=45.2,
            biome="Amazon Rainforest",
            land_use="Forest",
        ),
        Hotspot(
            id="FIRMS_87654321",
            latitude=-8.12345,
            longitude=-55.54321,
            acquisition_date=datetime.now() - timedelta(days=2),
            confidence=90,
            source="MODIS",
            brightness=310.5,
            frp=38.7,
            biome="Amazon Rainforest",
            land_use="Forest",
        ),
    ]


@pytest.mark.asyncio
@patch("api.presentation.controllers.hotspot_controller.HotspotRepository")
async def test_get_hotspots(mock_repository, test_client, mock_hotspots):
    """Testar endpoint GET /hotspots/."""
    # Configurar o mock do repositório
    mock_repo_instance = MagicMock()
    mock_repo_instance.find_by_criteria = AsyncMock(return_value=mock_hotspots)
    mock_repository.return_value = mock_repo_instance
    
    # Fazer requisição ao endpoint
    response = test_client.get("/hotspots/")
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "FIRMS_12345678"
    assert data[1]["id"] == "FIRMS_87654321"
    
    # Verificar se o repositório foi chamado corretamente
    mock_repo_instance.find_by_criteria.assert_called_once()


@pytest.mark.asyncio
@patch("api.presentation.controllers.hotspot_controller.HotspotRepository")
async def test_get_hotspots_with_filters(mock_repository, test_client, mock_hotspots):
    """Testar endpoint GET /hotspots/ com filtros."""
    # Configurar o mock do repositório
    mock_repo_instance = MagicMock()
    mock_repo_instance.find_by_criteria = AsyncMock(return_value=[mock_hotspots[0]])
    mock_repository.return_value = mock_repo_instance
    
    # Fazer requisição ao endpoint com filtros
    response = test_client.get(
        "/hotspots/?min_confidence=80&source=VIIRS&min_lon=-60&min_lat=-10&max_lon=-50&max_lat=0"
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "FIRMS_12345678"
    
    # Verificar se o repositório foi chamado corretamente com os filtros
    mock_repo_instance.find_by_criteria.assert_called_once()
    call_kwargs = mock_repo_instance.find_by_criteria.call_args.kwargs
    assert call_kwargs["min_confidence"] == 80
    assert call_kwargs["source"] == "VIIRS"
    assert call_kwargs["bounding_box"] == (-60, -10, -50, 0)


@pytest.mark.asyncio
@patch("api.presentation.controllers.hotspot_controller.HotspotRepository")
async def test_get_hotspots_empty_result(mock_repository, test_client):
    """Testar endpoint GET /hotspots/ com resultado vazio."""
    # Configurar o mock do repositório para retornar lista vazia
    mock_repo_instance = MagicMock()
    mock_repo_instance.find_by_criteria = AsyncMock(return_value=[])
    mock_repository.return_value = mock_repo_instance
    
    # Fazer requisição ao endpoint
    response = test_client.get("/hotspots/")
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
    
    # Verificar se o repositório foi chamado corretamente
    mock_repo_instance.find_by_criteria.assert_called_once()
