# Fluxo de Dados e Pipeline de Ingestão do GEIH

Este documento detalha o fluxo de dados e o pipeline de ingestão do Global Environmental Intelligence Hub (GEIH), descrevendo a arquitetura modular para integração de múltiplas fontes de dados ambientais.

## Visão Geral do Fluxo de Dados

O fluxo de dados do GEIH segue um modelo de pipeline modular, desde a ingestão de dados brutos até a disponibilização para análise e visualização:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Fontes    │ -> │  Ingestão   │ -> │Processamento│ -> │ Persistência│ -> │   Acesso    │
│  Externas   │    │  de Dados   │    │     ETL     │    │  de Dados   │    │  aos Dados  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Arquitetura de Ingestão de Dados

### Sistema de Conectores Plugáveis

O GEIH implementa um sistema de conectores plugáveis que permite a adição de novas fontes de dados com mínimo impacto no sistema existente:

```python
# Exemplo conceitual da interface base para conectores
class BaseConnector(ABC):
    """Interface base para todos os conectores de fontes de dados."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Estabelece conexão com a fonte de dados."""
        pass
    
    @abstractmethod
    async def fetch_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Busca dados da fonte com base nos parâmetros fornecidos."""
        pass
    
    @abstractmethod
    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """Valida os dados obtidos da fonte."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados sobre a fonte de dados."""
        pass
```

### Implementações de Conectores

Cada fonte de dados é implementada como um conector específico que herda da interface base:

```python
# Exemplo conceitual do conector NASA FIRMS
class NASAFirmsConnector(BaseConnector):
    """Conector para a API NASA FIRMS (Fire Information for Resource Management System)."""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    async def connect(self) -> bool:
        """Estabelece conexão com a API NASA FIRMS."""
        self.session = aiohttp.ClientSession()
        # Validação de credenciais e disponibilidade do serviço
        return True
    
    async def fetch_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Busca dados de focos de calor da API NASA FIRMS."""
        # Implementação da lógica de busca de dados
        # Suporte a diferentes formatos (CSV, GeoJSON, Shapefile)
        pass
    
    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """Valida os dados obtidos da API NASA FIRMS."""
        # Validação de estrutura, completude e consistência
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados sobre a fonte NASA FIRMS."""
        return {
            "name": "NASA FIRMS",
            "description": "Fire Information for Resource Management System",
            "data_types": ["hotspots", "burned_areas"],
            "spatial_coverage": "global",
            "temporal_resolution": "daily",
            "formats": ["csv", "geojson", "shapefile"]
        }
```

### Fábrica de Conectores

Uma fábrica de conectores gerencia a criação e o ciclo de vida dos conectores:

```python
# Exemplo conceitual da fábrica de conectores
class ConnectorFactory:
    """Fábrica para criação de instâncias de conectores."""
    
    _connectors = {}
    
    @classmethod
    def register_connector(cls, name: str, connector_class: Type[BaseConnector]):
        """Registra um tipo de conector na fábrica."""
        cls._connectors[name] = connector_class
    
    @classmethod
    def create_connector(cls, name: str, **kwargs) -> BaseConnector:
        """Cria uma instância de conector com base no nome registrado."""
        if name not in cls._connectors:
            raise ValueError(f"Connector '{name}' not registered")
        
        return cls._connectors[name](**kwargs)
    
    @classmethod
    def get_available_connectors(cls) -> List[str]:
        """Retorna a lista de conectores disponíveis."""
        return list(cls._connectors.keys())
```

## Pipeline de Ingestão com Apache Airflow

O GEIH utiliza Apache Airflow para orquestrar a ingestão de dados de múltiplas fontes, garantindo confiabilidade, agendamento e monitoramento:

### Estrutura de DAGs

```
data_pipeline/
├── dags/
│   ├── nasa_firms_dag.py       # DAG para ingestão de dados NASA FIRMS
│   ├── inpe_queimadas_dag.py   # DAG para ingestão de dados INPE BDQueimadas
│   └── ...
├── operators/
│   ├── connector_operator.py   # Operador personalizado para conectores
│   └── ...
└── utils/
    ├── validators.py           # Utilitários para validação de dados
    └── transformers.py         # Utilitários para transformação de dados
```

### Exemplo de DAG para NASA FIRMS

```python
# Exemplo conceitual de DAG para ingestão de dados NASA FIRMS
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

from operators.connector_operator import ConnectorOperator
from utils.validators import validate_geospatial_data
from utils.transformers import transform_to_standard_format

default_args = {
    'owner': 'geih',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'nasa_firms_ingestion',
    default_args=default_args,
    description='Ingestão de dados de focos de calor da NASA FIRMS',
    schedule_interval='@daily',
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=['nasa', 'firms', 'hotspots'],
)

# Tarefa para ingestão de dados
ingest_task = ConnectorOperator(
    task_id='ingest_nasa_firms_data',
    connector_name='nasa_firms',
    connector_params={
        'api_key': '{{ var.value.nasa_firms_api_key }}',
        'base_url': 'https://firms.modaps.eosdis.nasa.gov/api/area',
    },
    query_params={
        'region': 'amazon',
        'date_range': '{{ macros.ds_add(ds, -1) }}/{{ ds }}',
        'format': 'geojson',
    },
    output_path='{{ var.value.data_lake_path }}/raw/nasa_firms/{{ ds }}',
    dag=dag,
)

# Tarefa para validação de dados
validate_task = PythonOperator(
    task_id='validate_nasa_firms_data',
    python_callable=validate_geospatial_data,
    op_kwargs={
        'input_path': '{{ var.value.data_lake_path }}/raw/nasa_firms/{{ ds }}',
        'validation_rules': {
            'required_fields': ['latitude', 'longitude', 'acq_date', 'confidence'],
            'spatial_bounds': [-85, -60, 15, 20],  # Amazônia Legal + buffer
        },
    },
    dag=dag,
)

# Tarefa para transformação de dados
transform_task = PythonOperator(
    task_id='transform_nasa_firms_data',
    python_callable=transform_to_standard_format,
    op_kwargs={
        'input_path': '{{ var.value.data_lake_path }}/raw/nasa_firms/{{ ds }}',
        'output_path': '{{ var.value.data_lake_path }}/processed/hotspots/{{ ds }}',
        'schema': 'hotspots_schema',
    },
    dag=dag,
)

# Definição do fluxo de tarefas
ingest_task >> validate_task >> transform_task
```

## Fluxo de Processamento de Dados

### Etapas do Pipeline

1. **Ingestão**: Coleta de dados brutos das fontes externas
2. **Validação**: Verificação de integridade, completude e consistência
3. **Transformação**: Conversão para formato padrão do GEIH
4. **Enriquecimento**: Adição de metadados e informações contextuais
5. **Agregação**: Combinação de dados de múltiplas fontes
6. **Persistência**: Armazenamento em data lake e banco de dados
7. **Indexação**: Otimização para consultas e análises

### Processadores Modulares

O GEIH implementa processadores modulares para diferentes tipos de dados:

```python
# Exemplo conceitual da interface base para processadores
class BaseProcessor(ABC):
    """Interface base para todos os processadores de dados."""
    
    @abstractmethod
    async def process(self, data: Any) -> Any:
        """Processa os dados de acordo com a lógica específica."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados sobre o processador."""
        pass
```

### Implementações de Processadores

```python
# Exemplo conceitual do processador geoespacial
class GeospatialProcessor(BaseProcessor):
    """Processador para dados geoespaciais."""
    
    def __init__(self, crs: str = "EPSG:4326"):
        self.crs = crs
    
    async def process(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Processa dados geoespaciais."""
        # Reprojeção para CRS padrão
        if data.crs != self.crs:
            data = data.to_crs(self.crs)
        
        # Validação de geometrias
        data = data[~data.geometry.is_empty]
        data = data[data.geometry.is_valid]
        
        # Simplificação de geometrias complexas
        if "geometry" in data.columns:
            data["geometry"] = data.geometry.simplify(tolerance=0.0001)
        
        return data
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados sobre o processador geoespacial."""
        return {
            "name": "GeospatialProcessor",
            "description": "Processador para dados geoespaciais",
            "crs": self.crs,
        }
```

## Armazenamento e Persistência de Dados

### Estrutura do Data Lake

O GEIH utiliza uma estrutura de data lake organizada por camadas:

```
data_lake/
├── raw/                # Dados brutos, exatamente como recebidos das fontes
│   ├── nasa_firms/
│   ├── inpe_queimadas/
│   └── ...
├── processed/          # Dados processados e padronizados
│   ├── hotspots/
│   ├── burned_areas/
│   └── ...
├── enriched/           # Dados enriquecidos com informações adicionais
│   ├── hotspots_with_biomes/
│   └── ...
└── analytics/          # Dados agregados e otimizados para análise
    ├── daily_hotspots_by_region/
    └── ...
```

### Modelo de Dados PostgreSQL/PostGIS

O GEIH utiliza PostgreSQL com extensão PostGIS para armazenamento de dados geoespaciais:

```sql
-- Exemplo conceitual de esquema para focos de calor
CREATE TABLE hotspots (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    source_id VARCHAR(100),
    acquisition_date TIMESTAMP NOT NULL,
    confidence INTEGER,
    frp FLOAT,  -- Fire Radiative Power
    geom GEOMETRY(POINT, 4326) NOT NULL,
    biome VARCHAR(50),
    land_use VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para otimização de consultas
CREATE INDEX idx_hotspots_acquisition_date ON hotspots(acquisition_date);
CREATE INDEX idx_hotspots_source ON hotspots(source);
CREATE INDEX idx_hotspots_biome ON hotspots(biome);
CREATE INDEX idx_hotspots_geom ON hotspots USING GIST(geom);
```

## Integração com Serviços de Alerta

### Fluxo de Geração de Alertas

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Detecção   │ -> │  Análise de │ -> │  Geração de │ -> │ Disseminação│
│  de Eventos │    │    Risco    │    │   Alertas   │    │  de Alertas │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Modelo de Dados para Alertas

```sql
-- Exemplo conceitual de esquema para alertas
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,  -- fire, flood, deforestation, etc.
    severity VARCHAR(20) NOT NULL,  -- low, medium, high, critical
    title VARCHAR(200) NOT NULL,
    description TEXT,
    geom GEOMETRY(POLYGON, 4326) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(20) NOT NULL,  -- active, resolved, expired
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para assinaturas de alertas
CREATE TABLE alert_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    alert_type VARCHAR(50),  -- NULL significa todos os tipos
    geom GEOMETRY(POLYGON, 4326),  -- área de interesse
    min_severity VARCHAR(20) DEFAULT 'medium',
    notification_channel VARCHAR(50) NOT NULL,  -- email, push, sms, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Escalabilidade e Extensibilidade

O pipeline de ingestão do GEIH é projetado para escalar em várias dimensões:

1. **Escala de Volume**: Capacidade de processar grandes volumes de dados via processamento distribuído
2. **Escala de Fontes**: Facilidade de adicionar novas fontes via conectores plugáveis
3. **Escala de Processamento**: Capacidade de adicionar novos processadores para diferentes tipos de dados
4. **Escala Geográfica**: Expansão da cobertura geográfica sem alterações arquiteturais

### Estratégias de Escalabilidade

- **Particionamento de Dados**: Divisão de dados por região e período
- **Processamento Paralelo**: Execução simultânea de tarefas independentes
- **Caching Inteligente**: Armazenamento em cache de resultados frequentemente acessados
- **Processamento Incremental**: Ingestão apenas de dados novos ou alterados

## Monitoramento e Observabilidade

O pipeline de ingestão inclui monitoramento abrangente:

- **Métricas de Desempenho**: Tempo de execução, volume de dados, taxa de sucesso
- **Alertas Operacionais**: Notificações para falhas e anomalias
- **Logs Estruturados**: Registro detalhado de eventos e erros
- **Rastreamento de Linhagem**: Acompanhamento da origem e transformações dos dados

## Diagrama de Fluxo Completo

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Fontes de Dados Externas                        │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │NASA FIRMS│   │   INPE   │   │   ANA    │   │  AQICN   │   │   ...    ││
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘│
└───────┼──────────────┼──────────────┼──────────────┼──────────────┼──────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Sistema de Conectores Plugáveis                     │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │ Conector │   │ Conector │   │ Conector │   │ Conector │   │ Conector ││
│  │   FIRMS  │   │   INPE   │   │    ANA   │   │  AQICN   │   │   ...    ││
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘│
└───────┼──────────────┼──────────────┼──────────────┼──────────────┼──────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Apache Airflow (Orquestração)                     │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │  DAG de  │   │  DAG de  │   │  DAG de  │   │  DAG de  │   │  DAG de  ││
│  │ Ingestão │   │Validação │   │Transform.│   │Enriquec. │   │Persistên.││
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘│
└───────┼──────────────┼──────────────┼──────────────┼──────────────┼──────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Processadores Especializados                        │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │Processad.│   │Processad.│   │Processad.│   │Processad.│   │Processad.││
│  │Geoespacial│  │Temporal  │   │Estatíst. │   │  Imagem  │   │   ...    ││
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘│
└───────┼──────────────┼──────────────┼──────────────┼──────────────┼──────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Armazenamento de Dados                            │
│                                                                          │
│  ┌──────────┐                                          ┌──────────┐      │
│  │          │                                          │          │      │
│  │ Data Lake│◄────────────────────────────────────────┤PostgreSQL│      │
│  │  (MinIO) │                                          │ PostGIS  │      │
│  │          │                                          │          │      │
│  └────┬─────┘                                          └────┬─────┘      │
└───────┼──────────────────────────────────────────────────────┼──────────┘
         │                                                      │
         ▼                                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Serviços de Aplicação                             │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │ Serviço  │   │ Serviço  │   │ Serviço  │   │ Serviço  │   │ Serviço  ││
│  │de Análise│   │   de     │   │    de    │   │    de    │   │    de    ││
│  │          │   │Visualiz. │   │ Alertas  │   │Previsão  │   │   API    ││
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘│
└───────┼──────────────┼──────────────┼──────────────┼──────────────┼──────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Interfaces de Usuário                             │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │Dashboard │   │   Mapas  │   │ Alertas  │   │   API    │   │Exportação││
│  │Interativo│   │Geoespacial│  │  Push    │   │  Pública │   │  Dados   ││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

Este fluxo de dados e pipeline de ingestão foi projetado para atender aos requisitos de monitoramento contínuo e análise preditiva do GEIH, com foco inicial na Amazônia Legal e capacidade de expansão global. A arquitetura modular e plugável permite a adição de novas fontes de dados e funcionalidades com mínimo impacto no sistema existente.
