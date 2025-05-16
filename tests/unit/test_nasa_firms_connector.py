"""Testes para o conector NASA FIRMS."""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from data_ingestion.connectors.nasa_firms_connector import NASAFirmsConnector


@pytest.fixture
def mock_response():
    """Criar um objeto de resposta simulado."""
    mock = MagicMock()
    mock.status = 200
    mock.headers = {"Content-Type": "application/json"}
    mock.json = AsyncMock(return_value={"features": []})
    mock.text = AsyncMock(return_value="latitude,longitude\n-12.34,56.78")
    mock.read = AsyncMock(return_value=b"binary data")
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_session(mock_response):
    """Criar um objeto de sessão simulado."""
    mock = MagicMock()
    mock.get = MagicMock(return_value=mock_response)
    mock.close = AsyncMock()
    return mock


@pytest.mark.asyncio
async def test_connect(mock_session):
    """Testar método connect."""
    with patch("aiohttp.ClientSession", return_value=mock_session):
        connector = NASAFirmsConnector(api_key="test_key")
        result = await connector.connect()
        assert result is True
        mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_data_json(mock_session, mock_response):
    """Testar método fetch_data com resposta JSON."""
    with patch("aiohttp.ClientSession", return_value=mock_session):
        connector = NASAFirmsConnector(api_key="test_key")
        await connector.connect()
        
        result = await connector.fetch_data({"area": "test", "date_range": "2025-05-01/2025-05-02"})
        
        assert result["format"] == "json"
        assert "data" in result
        assert result["data"] == {"features": []}


@pytest.mark.asyncio
async def test_fetch_data_csv(mock_session, mock_response):
    """Testar método fetch_data com resposta CSV."""
    # Modificar o mock para retornar CSV
    mock_response.headers = {"Content-Type": "text/csv"}
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        connector = NASAFirmsConnector(api_key="test_key")
        await connector.connect()
        
        result = await connector.fetch_data({"area": "test", "date_range": "2025-05-01/2025-05-02"})
        
        assert result["format"] == "csv"
        assert "data" in result
        assert "latitude,longitude" in result["data"]


@pytest.mark.asyncio
async def test_fetch_data_error(mock_session, mock_response):
    """Testar método fetch_data com erro."""
    # Modificar o mock para simular erro
    mock_response.status = 404
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        connector = NASAFirmsConnector(api_key="test_key")
        await connector.connect()
        
        result = await connector.fetch_data({"area": "test", "date_range": "2025-05-01/2025-05-02"})
        
        assert "error" in result
        assert "404" in result["error"]


@pytest.mark.asyncio
async def test_validate_data_json():
    """Testar método validate_data com dados JSON."""
    connector = NASAFirmsConnector(api_key="test_key")
    
    # Dados válidos
    valid_data = {"format": "json", "data": {"features": []}}
    assert await connector.validate_data(valid_data) is True
    
    # Dados inválidos
    invalid_data = {"format": "json", "data": {}}
    assert await connector.validate_data(invalid_data) is False
    
    # Dados de erro
    error_data = {"error": "API error"}
    assert await connector.validate_data(error_data) is False


@pytest.mark.asyncio
async def test_validate_data_csv():
    """Testar método validate_data com dados CSV."""
    connector = NASAFirmsConnector(api_key="test_key")
    
    # Dados válidos
    valid_data = {"format": "csv", "data": "latitude,longitude\n-12.34,56.78"}
    assert await connector.validate_data(valid_data) is True
    
    # Dados inválidos
    invalid_data = {"format": "csv", "data": "header1,header2\n"}
    assert await connector.validate_data(invalid_data) is False


def test_get_metadata():
    """Testar método get_metadata."""
    connector = NASAFirmsConnector(api_key="test_key")
    metadata = connector.get_metadata()
    
    assert metadata["name"] == "NASA FIRMS"
    assert "description" in metadata
    assert "data_types" in metadata
    assert "spatial_coverage" in metadata
    assert "temporal_resolution" in metadata
    assert "formats" in metadata
