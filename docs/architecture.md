# Arquitetura do Global Environmental Intelligence Hub (GEIH)

## Arquitetura Limpa e Hexagonal (Ports & Adapters)

O GEIH adota uma arquitetura limpa e hexagonal (ports & adapters) para garantir modularidade, testabilidade e escalabilidade. Esta arquitetura permite a separação clara de responsabilidades e facilita a evolução independente de cada componente do sistema.

### Princípios Fundamentais

1. **Independência de Frameworks**: O núcleo da aplicação não depende de frameworks externos.
2. **Testabilidade**: Componentes podem ser testados isoladamente.
3. **Independência de UI**: A interface do usuário pode ser alterada sem afetar o restante do sistema.
4. **Independência de Banco de Dados**: A lógica de negócio não depende do mecanismo de persistência.
5. **Independência de Agentes Externos**: O núcleo da aplicação não conhece o mundo exterior.

### Camadas da Arquitetura

#### 1. Camada de Domínio (Core)

Representa o coração do sistema, contendo:

- **Entidades**: Objetos de negócio com regras e dados (ex: Alerta, EventoAmbiental, AreaMonitorada)
- **Regras de Negócio**: Lógica essencial independente de casos de uso específicos
- **Value Objects**: Objetos imutáveis que representam conceitos do domínio
- **Enums e Constantes**: Valores fixos do domínio

Esta camada não possui dependências externas e define interfaces (ports) que serão implementadas por camadas externas.

#### 2. Camada de Aplicação

Orquestra o fluxo de dados e coordena atividades:

- **Casos de Uso**: Implementações específicas de funcionalidades do sistema
- **Serviços de Aplicação**: Orquestram múltiplos casos de uso
- **DTOs (Data Transfer Objects)**: Objetos para transferência de dados entre camadas
- **Interfaces de Repositório**: Definem contratos para acesso a dados
- **Interfaces de Serviços Externos**: Definem contratos para serviços externos

#### 3. Camada de Infraestrutura

Implementa interfaces definidas nas camadas internas:

- **Adaptadores de Persistência**: Implementações de repositórios (PostgreSQL, PostGIS)
- **Adaptadores de Serviços Externos**: Implementações para APIs externas (NASA, INPE)
- **Configurações**: Setup de frameworks e bibliotecas
- **Implementações de Segurança**: Autenticação, autorização
- **Logging e Monitoramento**: Implementações de observabilidade

#### 4. Camada de Apresentação

Responsável pela interação com usuários e sistemas externos:

- **APIs REST/GraphQL**: Endpoints para acesso aos dados e funcionalidades
- **Controllers**: Manipulam requisições e respostas
- **Middlewares**: Processam requisições antes de chegarem aos controllers
- **Serializers/Deserializers**: Convertem dados entre formatos
- **Documentação da API**: Swagger/OpenAPI

#### 5. Camada de Interface do Usuário

Implementa as interfaces visuais:

- **Dashboards**: Visualizações interativas de dados
- **Mapas**: Representações geoespaciais
- **Componentes de UI**: Elementos reutilizáveis
- **Estados e Gerenciamento**: Lógica de apresentação

### Fluxo de Dados

1. Requisições externas chegam através da camada de apresentação
2. Controllers validam e transformam dados de entrada
3. Casos de uso na camada de aplicação orquestram a lógica
4. Entidades na camada de domínio aplicam regras de negócio
5. Adaptadores na camada de infraestrutura interagem com sistemas externos
6. Resultados fluem de volta através das camadas até o solicitante

### Comunicação Entre Camadas

- **Injeção de Dependência**: Implementações concretas são injetadas em tempo de execução
- **Inversão de Controle**: Dependências fluem de fora para dentro
- **Princípio da Dependência**: Dependências apontam para dentro (camadas externas dependem de camadas internas)

## Estrutura Modular e Plugável

O GEIH implementa uma estrutura modular que permite a adição de novas fontes de dados e funcionalidades com mínimo impacto no sistema existente.

### Conectores de Fontes de Dados

Cada fonte de dados é encapsulada em seu próprio módulo:

```
data_ingestion/
├── connectors/
│   ├── base_connector.py       # Interface base para todos os conectores
│   ├── nasa_firms_connector.py # Conector específico para NASA FIRMS
│   ├── inpe_connector.py       # Conector específico para INPE
│   └── ...
├── factories/
│   └── connector_factory.py    # Fábrica para criar instâncias de conectores
└── services/
    └── ingestion_service.py    # Serviço que orquestra a ingestão de dados
```

### Pipeline de Processamento

O pipeline de processamento segue uma abordagem modular:

```
data_pipeline/
├── processors/
│   ├── base_processor.py       # Interface base para processadores
│   ├── geospatial_processor.py # Processador para dados geoespaciais
│   ├── time_series_processor.py # Processador para séries temporais
│   └── ...
├── transformers/
│   ├── base_transformer.py     # Interface base para transformadores
│   └── ...
└── validators/
    ├── base_validator.py       # Interface base para validadores
    └── ...
```

### Modelos de IA

A estrutura para modelos de IA é projetada para permitir a integração futura de modelos avançados:

```
ai_models/
├── interfaces/
│   ├── model_interface.py      # Interface para todos os modelos
│   └── prediction_interface.py # Interface para predições
├── factories/
│   └── model_factory.py        # Fábrica para criar instâncias de modelos
├── registry/
│   └── model_registry.py       # Registro de modelos disponíveis
└── services/
    └── prediction_service.py   # Serviço que orquestra predições
```

## Escalabilidade e Extensibilidade

A arquitetura do GEIH é projetada para escalar em várias dimensões:

1. **Escala Geográfica**: De Amazônia para global
2. **Escala de Fontes de Dados**: Adição de novas fontes via conectores plugáveis
3. **Escala de Modelos**: Integração de modelos mais complexos via interfaces padronizadas
4. **Escala de Usuários**: Suporte a crescente base de usuários via APIs otimizadas

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                      Interface do Usuário                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Dashboards │  │    Mapas    │  │ Componentes Interativos │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    Camada de Apresentação                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  API REST   │  │  GraphQL    │  │      Documentação       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     Camada de Aplicação                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Casos de Uso│  │  Serviços   │  │        DTOs             │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      Camada de Domínio                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Entidades  │  │ Value Objects│ │    Regras de Negócio    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    Camada de Infraestrutura                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │Repositórios │  │  Adaptadores│  │      Serviços Externos  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

Esta arquitetura garante que o GEIH seja:
- Facilmente testável
- Altamente modular
- Preparado para evolução
- Resistente a mudanças tecnológicas
- Escalável para atender demandas futuras
