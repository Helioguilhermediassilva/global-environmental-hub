# Guia de Configuração do Repositório GitHub

Este guia fornece instruções passo a passo para configurar o projeto Global Environmental Intelligence Hub (GEIH) em um novo repositório no GitHub.

## 1. Criação do Repositório

1. Acesse sua conta GitHub em https://github.com/Helioguilhermediassilva
2. Clique no botão "New" para criar um novo repositório
3. Configure o repositório:
   - Nome: `global-environmental-hub`
   - Descrição: "Plataforma de código aberto para monitoramento ambiental e análise preditiva com IA"
   - Visibilidade: Public
   - Inicialize com: README (opcional, pois substituiremos depois)
   - Adicione uma licença MIT
4. Clique em "Create repository"

## 2. Configuração Local

### Clonando o Repositório

```bash
# Clone o repositório vazio
git clone https://github.com/Helioguilhermediassilva/global-environmental-hub.git
cd global-environmental-hub

# Ou, se você já tem arquivos locais:
git init
git remote add origin https://github.com/Helioguilhermediassilva/global-environmental-hub.git
```

### Estrutura de Diretórios

Crie a estrutura de diretórios básica:

```bash
# Criar diretórios principais
mkdir -p data_ingestion/{connectors,factories,services}
mkdir -p data_pipeline/{dags,operators,processors,utils}
mkdir -p api/{domain,application,infrastructure,presentation}
mkdir -p ai_models/{data,experiments,models,notebooks,src}
mkdir -p dashboards/{public,src,components}
mkdir -p infra/{docker,terraform,prometheus,grafana}
mkdir -p tests/{unit,integration,e2e}
mkdir -p docs
mkdir -p notebooks
mkdir -p .github/workflows
```

## 3. Adicionando Arquivos Iniciais

### Arquivos de Configuração

Crie os seguintes arquivos de configuração:

```bash
# .gitignore
cat > .gitignore << 'EOL'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/
.hypothesis/
.pytest_cache/
cover/

# Virtual Environment
venv/
ENV/
env/

# Jupyter Notebook
.ipynb_checkpoints

# Node.js
node_modules/
npm-debug.log
yarn-error.log
.pnp/
.pnp.js
coverage/
build/

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Data
*.csv
*.parquet
*.sqlite
*.db

# Logs
logs/
*.log

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Docker
.docker/

# Terraform
.terraform/
*.tfstate
*.tfstate.backup
*.tfvars

# MLflow
mlruns/

# DVC
.dvc/
EOL

# requirements.txt
cat > requirements.txt << 'EOL'
fastapi>=0.95.0
uvicorn>=0.21.1
pydantic>=1.10.7
sqlalchemy>=2.0.9
geoalchemy2>=0.13.0
psycopg2-binary>=2.9.6
alembic>=1.10.3
python-jose>=3.3.0
passlib>=1.7.4
python-multipart>=0.0.6
pandas>=2.0.0
geopandas>=0.12.2
numpy>=1.24.2
scikit-learn>=1.2.2
matplotlib>=3.7.1
seaborn>=0.12.2
requests>=2.28.2
aiohttp>=3.8.4
loguru>=0.6.0
prometheus-client>=0.16.0
opentelemetry-api>=1.16.0
opentelemetry-sdk>=1.16.0
opentelemetry-exporter-jaeger>=1.16.0
minio>=7.1.14
apache-airflow>=2.6.0
mlflow>=2.3.0
dvc>=2.58.0
pytest>=7.3.1
pytest-cov>=4.1.0
black>=23.3.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.2.0
EOL

# requirements-dev.txt
cat > requirements-dev.txt << 'EOL'
-r requirements.txt
pytest>=7.3.1
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
black>=23.3.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.2.0
bandit>=1.7.5
safety>=2.3.5
pre-commit>=3.2.2
sphinx>=6.1.3
sphinx-rtd-theme>=1.2.0
myst-parser>=1.0.0
EOL

# pyproject.toml
cat > pyproject.toml << 'EOL'
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["*/migrations/*", "venv/*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
python_classes = "Test*"
addopts = "--cov=. --cov-report=term --cov-report=xml --cov-report=html"
markers = [
    "unit: marks tests as unit tests",
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests",
    "slow: marks tests as slow",
]
EOL

# docker-compose.yml
cat > docker-compose.yml << 'EOL'
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.api
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=geih_dev
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - MINIO_HOST=minio
      - MINIO_PORT=9000
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
    depends_on:
      - postgres
      - redis
      - minio

  postgres:
    image: postgis/postgis:14-3.3
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_DB=geih_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  dashboard:
    build:
      context: ./dashboards
      dockerfile: ../infra/docker/Dockerfile.dashboard.dev
    volumes:
      - ./dashboards:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - NODE_ENV=development
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
  minio_data:
EOL

# Dockerfile para API
mkdir -p infra/docker
cat > infra/docker/Dockerfile.api << 'EOL'
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código-fonte
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOL

# Dockerfile para Dashboard (dev)
cat > infra/docker/Dockerfile.dashboard.dev << 'EOL'
FROM node:20-alpine

WORKDIR /app

# Instalar dependências
COPY package*.json ./
RUN npm install

# Copiar código-fonte
COPY . .

# Expor porta
EXPOSE 3000

# Comando para iniciar a aplicação em modo de desenvolvimento
CMD ["npm", "start"]
EOL

# GitHub Actions CI workflow
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'EOL'
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Lint with flake8
        run: flake8 .
      - name: Check formatting with black
        run: black --check .
      - name: Check imports with isort
        run: isort --check .

  test:
    name: Test
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:14-3.3
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_USER: postgres
          POSTGRES_DB: test_geih
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Run Python tests
        run: pytest
        env:
          POSTGRES_HOST: localhost
          POSTGRES_PORT: 5432
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_geih
EOL
```

### Arquivos de Código Iniciais

Crie os seguintes arquivos de código iniciais:

```bash
# API - Arquivo principal
mkdir -p api
cat > api/__init__.py << 'EOL'
"""Global Environmental Intelligence Hub API."""
EOL

cat > api/main.py << 'EOL'
"""Main module for the GEIH API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Global Environmental Intelligence Hub API",
    description="API for environmental monitoring and predictive analysis",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Global Environmental Intelligence Hub API"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
EOL

# Exemplo de conector para NASA FIRMS
mkdir -p data_ingestion/connectors
cat > data_ingestion/connectors/__init__.py << 'EOL'
"""Data ingestion connectors package."""
EOL

cat > data_ingestion/connectors/base_connector.py << 'EOL'
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
EOL

cat > data_ingestion/connectors/nasa_firms_connector.py << 'EOL'
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
EOL

# Exemplo de DAG para Airflow
mkdir -p data_pipeline/dags
cat > data_pipeline/dags/nasa_firms_ingestion.py << 'EOL'
"""DAG for NASA FIRMS data ingestion."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "geih",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


def ingest_nasa_firms_data(**kwargs):
    """Ingest data from NASA FIRMS API."""
    # This is a placeholder function
    # In a real implementation, this would use the NASAFirmsConnector
    print("Ingesting NASA FIRMS data")
    return {"status": "success", "records": 100}


def validate_nasa_firms_data(**kwargs):
    """Validate NASA FIRMS data."""
    # This is a placeholder function
    print("Validating NASA FIRMS data")
    return {"status": "success", "valid_records": 98, "invalid_records": 2}


def transform_nasa_firms_data(**kwargs):
    """Transform NASA FIRMS data to standard format."""
    # This is a placeholder function
    print("Transforming NASA FIRMS data")
    return {"status": "success", "transformed_records": 98}


with DAG(
    "nasa_firms_ingestion",
    default_args=default_args,
    description="Ingest data from NASA FIRMS API",
    schedule_interval="@daily",
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=["nasa", "firms", "hotspots"],
) as dag:
    ingest_task = PythonOperator(
        task_id="ingest_nasa_firms_data",
        python_callable=ingest_nasa_firms_data,
    )

    validate_task = PythonOperator(
        task_id="validate_nasa_firms_data",
        python_callable=validate_nasa_firms_data,
    )

    transform_task = PythonOperator(
        task_id="transform_nasa_firms_data",
        python_callable=transform_nasa_firms_data,
    )

    # Define task dependencies
    ingest_task >> validate_task >> transform_task
EOL

# Exemplo de teste unitário
mkdir -p tests/unit
cat > tests/unit/__init__.py << 'EOL'
"""Unit tests package."""
EOL

cat > tests/unit/test_nasa_firms_connector.py << 'EOL'
"""Tests for NASA FIRMS connector."""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from data_ingestion.connectors.nasa_firms_connector import NASAFirmsConnector


@pytest.fixture
def mock_response():
    """Create a mock response object."""
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
    """Create a mock session object."""
    mock = MagicMock()
    mock.get = MagicMock(return_value=mock_response)
    mock.close = AsyncMock()
    return mock


@pytest.mark.asyncio
async def test_connect(mock_session):
    """Test connect method."""
    with patch("aiohttp.ClientSession", return_value=mock_session):
        connector = NASAFirmsConnector(api_key="test_key")
        result = await connector.connect()
        assert result is True
        mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_data_json(mock_session, mock_response):
    """Test fetch_data method with JSON response."""
    with patch("aiohttp.ClientSession", return_value=mock_session):
        connector = NASAFirmsConnector(api_key="test_key")
        await connector.connect()
        
        result = await connector.fetch_data({"area": "test", "date_range": "2025-05-01/2025-05-02"})
        
        assert result["format"] == "json"
        assert "data" in result
        assert result["data"] == {"features": []}


@pytest.mark.asyncio
async def test_validate_data_json():
    """Test validate_data method with JSON data."""
    connector = NASAFirmsConnector(api_key="test_key")
    
    # Valid data
    valid_data = {"format": "json", "data": {"features": []}}
    assert await connector.validate_data(valid_data) is True
    
    # Invalid data
    invalid_data = {"format": "json", "data": {}}
    assert await connector.validate_data(invalid_data) is False
    
    # Error data
    error_data = {"error": "API error"}
    assert await connector.validate_data(error_data) is False


def test_get_metadata():
    """Test get_metadata method."""
    connector = NASAFirmsConnector(api_key="test_key")
    metadata = connector.get_metadata()
    
    assert metadata["name"] == "NASA FIRMS"
    assert "description" in metadata
    assert "data_types" in metadata
    assert "spatial_coverage" in metadata
    assert "temporal_resolution" in metadata
    assert "formats" in metadata
EOL

# Exemplo de modelo de domínio
mkdir -p api/domain/entities
cat > api/domain/entities/__init__.py << 'EOL'
"""Domain entities package."""
EOL

cat > api/domain/entities/hotspot.py << 'EOL'
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
EOL

# Exemplo de caso de uso
mkdir -p api/application/use_cases
cat > api/application/use_cases/__init__.py << 'EOL'
"""Application use cases package."""
EOL

cat > api/application/use_cases/get_hotspots.py << 'EOL'
"""Use case for retrieving hotspots."""
from datetime import datetime
from typing import List, Optional

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
        bounding_box: Optional[tuple] = None,
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
        # This is a placeholder implementation
        # In a real implementation, this would use the repository to fetch data
        return await self.hotspot_repository.find_by_criteria(
            start_date=start_date,
            end_date=end_date,
            min_confidence=min_confidence,
            source=source,
            biome=biome,
            bounding_box=bounding_box,
        )
EOL

# Exemplo de repositório
mkdir -p api/infrastructure/repositories
cat > api/infrastructure/repositories/__init__.py << 'EOL'
"""Infrastructure repositories package."""
EOL

cat > api/infrastructure/repositories/hotspot_repository.py << 'EOL'
"""Repository for hotspot data access."""
from datetime import datetime
from typing import List, Optional

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
        bounding_box: Optional[tuple] = None,
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
EOL

# Exemplo de modelo de banco de dados
mkdir -p api/infrastructure/models
cat > api/infrastructure/models/__init__.py << 'EOL'
"""Infrastructure database models package."""
EOL

cat > api/infrastructure/models/base.py << 'EOL'
"""Base model for SQLAlchemy models."""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
EOL

cat > api/infrastructure/models/hotspot_model.py << 'EOL'
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
EOL

# Exemplo de controller
mkdir -p api/presentation/controllers
cat > api/presentation/controllers/__init__.py << 'EOL'
"""Presentation controllers package."""
EOL

cat > api/presentation/controllers/hotspot_controller.py << 'EOL'
"""Controller for hotspot endpoints."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from api.application.use_cases.get_hotspots import GetHotspotsUseCase
from api.domain.entities.hotspot import Hotspot
from api.infrastructure.repositories.hotspot_repository import HotspotRepository
from api.presentation.dependencies.database import get_db_session

router = APIRouter(prefix="/hotspots", tags=["hotspots"])


@router.get("/", response_model=List[Hotspot])
async def get_hotspots(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering hotspots"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering hotspots"),
    min_confidence: Optional[int] = Query(None, description="Minimum confidence level"),
    source: Optional[str] = Query(None, description="Source of the data (e.g., MODIS, VIIRS)"),
    biome: Optional[str] = Query(None, description="Biome filter"),
    min_lon: Optional[float] = Query(None, description="Minimum longitude for bounding box"),
    min_lat: Optional[float] = Query(None, description="Minimum latitude for bounding box"),
    max_lon: Optional[float] = Query(None, description="Maximum longitude for bounding box"),
    max_lat: Optional[float] = Query(None, description="Maximum latitude for bounding box"),
    session=Depends(get_db_session),
):
    """Get hotspots based on criteria."""
    # Create bounding box if coordinates are provided
    bounding_box = None
    if all(coord is not None for coord in [min_lon, min_lat, max_lon, max_lat]):
        bounding_box = (min_lon, min_lat, max_lon, max_lat)

    # Create repository
    repository = HotspotRepository(session)
    
    # Create and execute use case
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
EOL

# Exemplo de dependências
mkdir -p api/presentation/dependencies
cat > api/presentation/dependencies/__init__.py << 'EOL'
"""Presentation dependencies package."""
EOL

cat > api/presentation/dependencies/database.py << 'EOL'
"""Database dependencies."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# This is a placeholder - in a real application, you would get these from environment variables
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@postgres/geih_dev"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session():
    """Get database session dependency."""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
EOL

# Atualizar o arquivo main.py para incluir os controllers
cat > api/main.py << 'EOL'
"""Main module for the GEIH API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.presentation.controllers.hotspot_controller import router as hotspot_router

app = FastAPI(
    title="Global Environmental Intelligence Hub API",
    description="API for environmental monitoring and predictive analysis",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(hotspot_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Global Environmental Intelligence Hub API"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
EOL

# Exemplo de dashboard React
mkdir -p dashboards/src
cat > dashboards/package.json << 'EOL'
{
  "name": "geih-dashboard",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^13.5.0",
    "@types/jest": "^27.5.2",
    "@types/node": "^16.18.23",
    "@types/react": "^18.0.35",
    "@types/react-dom": "^18.0.11",
    "axios": "^1.3.5",
    "leaflet": "^1.9.3",
    "@types/leaflet": "^1.9.3",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-leaflet": "^4.2.1",
    "react-router-dom": "^6.10.0",
    "react-scripts": "5.0.1",
    "typescript": "^4.9.5",
    "web-vitals": "^2.1.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject",
    "lint": "eslint src",
    "format": "prettier --write src",
    "format:check": "prettier --check src"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "devDependencies": {
    "@typescript-eslint/eslint-plugin": "^5.58.0",
    "@typescript-eslint/parser": "^5.58.0",
    "eslint": "^8.38.0",
    "eslint-config-prettier": "^8.8.0",
    "eslint-plugin-prettier": "^4.2.1",
    "eslint-plugin-react": "^7.32.2",
    "prettier": "^2.8.7"
  }
}
EOL

mkdir -p dashboards/public
cat > dashboards/public/index.html << 'EOL'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Global Environmental Intelligence Hub Dashboard"
    />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <link
      rel="stylesheet"
      href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css"
      integrity="sha256-kLaT2GOSpHechhsozzB+flnD+zUyjE2LlfWPgU04xyI="
      crossorigin=""
    />
    <title>GEIH Dashboard</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOL

cat > dashboards/public/manifest.json << 'EOL'
{
  "short_name": "GEIH",
  "name": "Global Environmental Intelligence Hub",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    },
    {
      "src": "logo192.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "logo512.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}
EOL

cat > dashboards/src/index.tsx << 'EOL'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

reportWebVitals();
EOL

cat > dashboards/src/index.css << 'EOL'
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
EOL

cat > dashboards/src/App.tsx << 'EOL'
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import MapPage from './pages/MapPage';
import DashboardPage from './pages/DashboardPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main className="App-main">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/map" element={<MapPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </main>
        <footer className="App-footer">
          <p>© 2025 Global Environmental Intelligence Hub</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
EOL

cat > dashboards/src/App.css << 'EOL'
.App {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.App-main {
  flex: 1;
  padding: 20px;
}

.App-footer {
  background-color: #f5f5f5;
  padding: 10px;
  text-align: center;
  font-size: 0.8rem;
}
EOL

mkdir -p dashboards/src/components
cat > dashboards/src/components/Header.tsx << 'EOL'
import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header: React.FC = () => {
  return (
    <header className="Header">
      <div className="Header-logo">
        <h1>GEIH</h1>
      </div>
      <nav className="Header-nav">
        <ul>
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/map">Map</Link>
          </li>
          <li>
            <Link to="/dashboard">Dashboard</Link>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
EOL

cat > dashboards/src/components/Header.css << 'EOL'
.Header {
  background-color: #2c3e50;
  color: white;
  padding: 10px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.Header-logo h1 {
  margin: 0;
  font-size: 1.5rem;
}

.Header-nav ul {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.Header-nav li {
  margin-left: 20px;
}

.Header-nav a {
  color: white;
  text-decoration: none;
  font-weight: 500;
}

.Header-nav a:hover {
  text-decoration: underline;
}
EOL

mkdir -p dashboards/src/pages
cat > dashboards/src/pages/HomePage.tsx << 'EOL'
import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage: React.FC = () => {
  return (
    <div className="HomePage">
      <section className="Hero">
        <div className="Hero-content">
          <h1>Global Environmental Intelligence Hub</h1>
          <p>
            Monitoring environmental data and providing predictive analysis for a sustainable future.
          </p>
          <div className="Hero-buttons">
            <Link to="/map" className="Button Button-primary">
              Explore Map
            </Link>
            <Link to="/dashboard" className="Button Button-secondary">
              View Dashboard
            </Link>
          </div>
        </div>
      </section>

      <section className="Features">
        <div className="Feature">
          <h2>Real-time Monitoring</h2>
          <p>
            Access real-time environmental data from multiple sources including NASA, INPE, and more.
          </p>
        </div>
        <div className="Feature">
          <h2>Predictive Analysis</h2>
          <p>
            Leverage AI models to predict environmental risks and trends.
          </p>
        </div>
        <div className="Feature">
          <h2>Alert System</h2>
          <p>
            Receive timely alerts about environmental events in your area of interest.
          </p>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
EOL

cat > dashboards/src/pages/HomePage.css << 'EOL'
.HomePage {
  display: flex;
  flex-direction: column;
}

.Hero {
  background-color: #3498db;
  color: white;
  padding: 60px 20px;
  text-align: center;
}

.Hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.Hero h1 {
  font-size: 2.5rem;
  margin-bottom: 20px;
}

.Hero p {
  font-size: 1.2rem;
  margin-bottom: 30px;
}

.Hero-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.Button {
  display: inline-block;
  padding: 10px 20px;
  border-radius: 4px;
  text-decoration: none;
  font-weight: bold;
  transition: background-color 0.3s;
}

.Button-primary {
  background-color: #2ecc71;
  color: white;
}

.Button-primary:hover {
  background-color: #27ae60;
}

.Button-secondary {
  background-color: white;
  color: #3498db;
}

.Button-secondary:hover {
  background-color: #f5f5f5;
}

.Features {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  padding: 40px 20px;
}

.Feature {
  flex: 1;
  min-width: 250px;
  max-width: 350px;
  margin: 20px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.Feature h2 {
  color: #2c3e50;
  margin-bottom: 15px;
}
EOL

cat > dashboards/src/pages/MapPage.tsx << 'EOL'
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import './MapPage.css';

interface Hotspot {
  id: string;
  latitude: number;
  longitude: number;
  acquisition_date: string;
  confidence: number;
  source: string;
}

const MapPage: React.FC = () => {
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // This is a placeholder - in a real application, you would fetch data from your API
    const fetchHotspots = async () => {
      try {
        // Simulating API call
        // In a real application: const response = await axios.get('/api/hotspots');
        
        // Simulated data
        const mockData: Hotspot[] = [
          {
            id: '1',
            latitude: -9.45678,
            longitude: -56.78901,
            acquisition_date: '2025-05-15T14:30:00',
            confidence: 85,
            source: 'VIIRS',
          },
          {
            id: '2',
            latitude: -8.12345,
            longitude: -55.54321,
            acquisition_date: '2025-05-15T15:45:00',
            confidence: 90,
            source: 'MODIS',
          },
          {
            id: '3',
            latitude: -10.98765,
            longitude: -57.12345,
            acquisition_date: '2025-05-15T16:15:00',
            confidence: 75,
            source: 'VIIRS',
          },
        ];
        
        setHotspots(mockData);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch hotspots data');
        setLoading(false);
      }
    };

    fetchHotspots();
  }, []);

  // Center of the Amazon rainforest
  const amazonCenter = [-3.4653, -62.2159];

  return (
    <div className="MapPage">
      <div className="MapControls">
        <h2>Fire Hotspots Map</h2>
        <div className="Filters">
          <div className="FilterGroup">
            <label htmlFor="date-range">Date Range:</label>
            <select id="date-range">
              <option value="1">Last 24 hours</option>
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
            </select>
          </div>
          <div className="FilterGroup">
            <label htmlFor="source">Source:</label>
            <select id="source">
              <option value="all">All Sources</option>
              <option value="MODIS">MODIS</option>
              <option value="VIIRS">VIIRS</option>
            </select>
          </div>
          <div className="FilterGroup">
            <label htmlFor="confidence">Min Confidence:</label>
            <select id="confidence">
              <option value="0">All</option>
              <option value="50">50%</option>
              <option value="75">75%</option>
              <option value="90">90%</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="MapContainer">
        {loading ? (
          <div className="Loading">Loading map data...</div>
        ) : error ? (
          <div className="Error">{error}</div>
        ) : (
          <MapContainer center={amazonCenter} zoom={5} style={{ height: '100%', width: '100%' }}>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {hotspots.map((hotspot) => (
              <Marker
                key={hotspot.id}
                position={[hotspot.latitude, hotspot.longitude]}
              >
                <Popup>
                  <div>
                    <h3>Hotspot {hotspot.id}</h3>
                    <p>Source: {hotspot.source}</p>
                    <p>Confidence: {hotspot.confidence}%</p>
                    <p>Date: {new Date(hotspot.acquisition_date).toLocaleString()}</p>
                    <p>
                      Location: {hotspot.latitude.toFixed(5)}, {hotspot.longitude.toFixed(5)}
                    </p>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        )}
      </div>
    </div>
  );
};

export default MapPage;
EOL

cat > dashboards/src/pages/MapPage.css << 'EOL'
.MapPage {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px);
}

.MapControls {
  padding: 15px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #ddd;
}

.MapControls h2 {
  margin-top: 0;
  margin-bottom: 15px;
}

.Filters {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.FilterGroup {
  display: flex;
  align-items: center;
}

.FilterGroup label {
  margin-right: 10px;
  font-weight: 500;
}

.FilterGroup select {
  padding: 5px 10px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.MapContainer {
  flex: 1;
  position: relative;
}

.Loading, .Error {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.8);
}

.Error {
  color: #e74c3c;
}
EOL

cat > dashboards/src/pages/DashboardPage.tsx << 'EOL'
import React from 'react';
import './DashboardPage.css';

const DashboardPage: React.FC = () => {
  return (
    <div className="DashboardPage">
      <h1>Environmental Dashboard</h1>
      
      <div className="Dashboard-grid">
        <div className="Dashboard-card">
          <h2>Fire Hotspots</h2>
          <div className="Dashboard-stat">
            <span className="Dashboard-stat-value">1,245</span>
            <span className="Dashboard-stat-label">Last 7 days</span>
          </div>
          <div className="Dashboard-chart">
            {/* Placeholder for chart */}
            <div className="Chart-placeholder">
              <div className="Bar" style={{ height: '30%' }}></div>
              <div className="Bar" style={{ height: '50%' }}></div>
              <div className="Bar" style={{ height: '70%' }}></div>
              <div className="Bar" style={{ height: '40%' }}></div>
              <div className="Bar" style={{ height: '60%' }}></div>
              <div className="Bar" style={{ height: '80%' }}></div>
              <div className="Bar" style={{ height: '45%' }}></div>
            </div>
          </div>
        </div>
        
        <div className="Dashboard-card">
          <h2>Deforestation Alerts</h2>
          <div className="Dashboard-stat">
            <span className="Dashboard-stat-value">328</span>
            <span className="Dashboard-stat-label">Last 30 days</span>
          </div>
          <div className="Dashboard-chart">
            {/* Placeholder for chart */}
            <div className="Chart-placeholder">
              <div className="Bar" style={{ height: '20%' }}></div>
              <div className="Bar" style={{ height: '35%' }}></div>
              <div className="Bar" style={{ height: '25%' }}></div>
              <div className="Bar" style={{ height: '40%' }}></div>
              <div className="Bar" style={{ height: '30%' }}></div>
              <div className="Bar" style={{ height: '45%' }}></div>
              <div className="Bar" style={{ height: '50%' }}></div>
            </div>
          </div>
        </div>
        
        <div className="Dashboard-card">
          <h2>Risk Forecast</h2>
          <div className="Dashboard-stat">
            <span className="Dashboard-stat-value">High</span>
            <span className="Dashboard-stat-label">Next 7 days</span>
          </div>
          <div className="Dashboard-chart">
            {/* Placeholder for chart */}
            <div className="Chart-placeholder">
              <div className="Line"></div>
            </div>
          </div>
        </div>
        
        <div className="Dashboard-card">
          <h2>Protected Areas</h2>
          <div className="Dashboard-stat">
            <span className="Dashboard-stat-value">42</span>
            <span className="Dashboard-stat-label">With active alerts</span>
          </div>
          <div className="Dashboard-chart">
            {/* Placeholder for chart */}
            <div className="Chart-placeholder">
              <div className="Pie"></div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="Dashboard-table-container">
        <h2>Recent Alerts</h2>
        <table className="Dashboard-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Location</th>
              <th>Severity</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>2025-05-15</td>
              <td>Fire</td>
              <td>Amazonas, Brazil</td>
              <td>High</td>
              <td>Active</td>
            </tr>
            <tr>
              <td>2025-05-14</td>
              <td>Deforestation</td>
              <td>Pará, Brazil</td>
              <td>Medium</td>
              <td>Verified</td>
            </tr>
            <tr>
              <td>2025-05-13</td>
              <td>Fire</td>
              <td>Rondônia, Brazil</td>
              <td>Critical</td>
              <td>Active</td>
            </tr>
            <tr>
              <td>2025-05-12</td>
              <td>Deforestation</td>
              <td>Mato Grosso, Brazil</td>
              <td>Low</td>
              <td>Resolved</td>
            </tr>
            <tr>
              <td>2025-05-11</td>
              <td>Fire</td>
              <td>Acre, Brazil</td>
              <td>Medium</td>
              <td>Resolved</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DashboardPage;
EOL

cat > dashboards/src/pages/DashboardPage.css << 'EOL'
.DashboardPage {
  padding: 20px;
}

.DashboardPage h1 {
  margin-bottom: 30px;
  color: #2c3e50;
}

.Dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.Dashboard-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.Dashboard-card h2 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.2rem;
  color: #2c3e50;
}

.Dashboard-stat {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

.Dashboard-stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #3498db;
}

.Dashboard-stat-label {
  font-size: 0.9rem;
  color: #7f8c8d;
}

.Dashboard-chart {
  height: 150px;
}

.Chart-placeholder {
  height: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.Bar {
  width: 12%;
  background-color: #3498db;
  border-radius: 3px 3px 0 0;
}

.Line {
  height: 2px;
  background-color: #e74c3c;
  position: relative;
  top: 50%;
}

.Line::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 50px;
  background: linear-gradient(to bottom, rgba(231, 76, 60, 0.2), transparent);
  bottom: 0;
}

.Pie {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: conic-gradient(
    #3498db 0% 25%,
    #2ecc71 25% 55%,
    #f1c40f 55% 70%,
    #e74c3c 70% 100%
  );
  margin: 0 auto;
}

.Dashboard-table-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.Dashboard-table-container h2 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.2rem;
  color: #2c3e50;
}

.Dashboard-table {
  width: 100%;
  border-collapse: collapse;
}

.Dashboard-table th,
.Dashboard-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.Dashboard-table th {
  background-color: #f5f5f5;
  font-weight: 600;
  color: #2c3e50;
}

.Dashboard-table tr:last-child td {
  border-bottom: none;
}

.Dashboard-table tr:hover {
  background-color: #f9f9f9;
}
EOL

cat > dashboards/src/reportWebVitals.ts << 'EOL'
import { ReportHandler } from 'web-vitals';

const reportWebVitals = (onPerfEntry?: ReportHandler) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;
EOL

# Criar LICENSE
cat > LICENSE << 'EOL'
MIT License

Copyright (c) 2025 Global Environmental Intelligence Hub

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOL
```

## 4. Commit e Push Inicial

Após criar todos os arquivos, faça o commit inicial e push para o GitHub:

```bash
# Adicionar todos os arquivos
git add .

# Commit inicial
git commit -m "Initial commit: Project structure and base files"

# Push para o GitHub
git push -u origin main
```

## 5. Configuração do GitHub

### Configurar Proteção de Branch

1. Acesse as configurações do repositório no GitHub
2. Vá para "Branches" > "Branch protection rules"
3. Clique em "Add rule"
4. Configure:
   - Branch name pattern: `main`
   - Require pull request reviews before merging
   - Require status checks to pass before merging
   - Include administrators
5. Salve as alterações

### Configurar GitHub Pages (opcional)

1. Acesse as configurações do repositório no GitHub
2. Vá para "Pages"
3. Configure:
   - Source: Deploy from a branch
   - Branch: `main`
   - Folder: `/docs`
4. Salve as alterações

### Configurar Secrets para GitHub Actions

1. Acesse as configurações do repositório no GitHub
2. Vá para "Secrets and variables" > "Actions"
3. Adicione os seguintes secrets:
   - `DOCKERHUB_USERNAME`: Seu nome de usuário do Docker Hub
   - `DOCKERHUB_TOKEN`: Seu token de acesso do Docker Hub

## 6. Desenvolvimento Local

### Iniciar o Ambiente de Desenvolvimento

```bash
# Construir e iniciar os containers
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Acessar o serviço API
curl http://localhost:8000/health

# Acessar o dashboard no navegador
# Abra http://localhost:3000
```

### Fluxo de Trabalho de Desenvolvimento

1. Crie uma branch para sua feature:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

2. Desenvolva e teste localmente:
   ```bash
   # Executar testes
   docker-compose exec api pytest

   # Verificar formatação
   docker-compose exec api black --check .
   ```

3. Commit e push:
   ```bash
   git add .
   git commit -m "feat: adiciona nova funcionalidade"
   git push origin feature/nova-funcionalidade
   ```

4. Crie um Pull Request no GitHub para a branch `develop`

5. Após aprovação e merge, atualize seu repositório local:
   ```bash
   git checkout develop
   git pull
   ```

## 7. Próximos Passos

1. **Implementar Conectores Adicionais**: Adicionar conectores para INPE e outras fontes de dados
2. **Desenvolver Modelos de ML**: Implementar modelos de risco de incêndio e detecção de desmatamento
3. **Expandir API**: Adicionar endpoints para alertas e análises
4. **Melhorar Dashboard**: Implementar visualizações interativas e filtros avançados
5. **Configurar Monitoramento**: Implementar Prometheus e Grafana para observabilidade

## 8. Recursos Adicionais

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [NASA FIRMS API Documentation](https://firms.modaps.eosdis.nasa.gov/api/)
