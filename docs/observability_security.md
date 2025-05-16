# Políticas de Observabilidade e Segurança do GEIH

Este documento detalha as políticas de observabilidade e segurança do Global Environmental Intelligence Hub (GEIH), descrevendo as práticas, ferramentas e configurações para garantir monitoramento eficaz, logging estruturado, segurança e conformidade com padrões relevantes.

## Observabilidade

A observabilidade no GEIH é implementada em múltiplas camadas para garantir visibilidade completa do sistema, facilitando diagnósticos, otimizações e resposta a incidentes.

### Logging Estruturado

O GEIH utiliza logging estruturado com Loguru e OpenTelemetry para capturar eventos do sistema de forma consistente e pesquisável:

#### Configuração de Logging

```python
# Exemplo conceitual de configuração de logging estruturado
import json
import sys
from datetime import datetime
from loguru import logger

# Configuração do formato de log estruturado
def log_format(record):
    """Formata registros de log em JSON estruturado."""
    log_record = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        "process_id": record["process"].id,
        "thread_id": record["thread"].id
    }
    
    # Adicionar exceção se presente
    if record["exception"]:
        log_record["exception"] = {
            "type": record["exception"].type.__name__,
            "value": str(record["exception"].value),
            "traceback": record["exception"].traceback
        }
    
    # Adicionar contexto extra
    if record["extra"]:
        log_record["context"] = record["extra"]
    
    return json.dumps(log_record)

# Configurar logger
logger.remove()  # Remover handler padrão
logger.add(
    sys.stdout,
    format=log_format,
    serialize=True,
    backtrace=True,
    diagnose=True,
    enqueue=True,
    level="INFO"
)

# Configurar arquivo de log rotativo
logger.add(
    "/var/log/geih/geih.log",
    format=log_format,
    serialize=True,
    rotation="50 MB",
    retention="30 days",
    compression="gz",
    level="DEBUG"
)

# Configurar logger para erros críticos com notificação
logger.add(
    lambda msg: notify_team(msg),
    format=log_format,
    filter=lambda record: record["level"].name == "CRITICAL",
    level="CRITICAL"
)

def notify_team(msg):
    """Notifica equipe sobre erros críticos."""
    # Implementação de notificação (e-mail, Slack, etc.)
    pass
```

#### Contexto de Logging

```python
# Exemplo conceitual de uso de contexto em logs
from loguru import logger

# Adicionar contexto global
logger.configure(extra={"service": "geih-api", "environment": "production"})

# Adicionar contexto de request
@app.middleware("http")
async def add_request_context(request, call_next):
    """Adiciona contexto de request aos logs."""
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    user_id = get_user_id_from_request(request)
    
    with logger.contextualize(request_id=request_id, user_id=user_id):
        logger.info(f"Recebida requisição {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Requisição concluída com status {response.status_code}")
        return response

# Uso em funções específicas
def process_data(data, source):
    """Processa dados com contexto de logging."""
    with logger.contextualize(data_source=source, data_size=len(data)):
        logger.info("Iniciando processamento de dados")
        try:
            # Processamento de dados
            result = transform_data(data)
            logger.info("Processamento concluído com sucesso", result_size=len(result))
            return result
        except Exception as e:
            logger.exception("Erro no processamento de dados")
            raise
```

### Métricas e Monitoramento

O GEIH utiliza Prometheus e Grafana para coleta, armazenamento e visualização de métricas:

#### Configuração do Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'geih-api'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['api:8000']
    
  - job_name: 'geih-data-pipeline'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['data-pipeline:9090']
    
  - job_name: 'geih-ml-service'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['ml-service:8080']
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

#### Instrumentação de Código

```python
# Exemplo conceitual de instrumentação com Prometheus
from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
import time

# Contadores para eventos
api_requests_total = Counter(
    'api_requests_total',
    'Total de requisições à API',
    ['method', 'endpoint', 'status']
)

# Histogramas para latência
api_request_duration = Histogram(
    'api_request_duration_seconds',
    'Duração das requisições à API',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)
)

# Gauges para valores atuais
active_users = Gauge(
    'active_users',
    'Número de usuários ativos no sistema'
)

# Summaries para estatísticas
data_processing_size = Summary(
    'data_processing_size_bytes',
    'Tamanho dos dados processados em bytes'
)

# Middleware para instrumentação de API
@app.middleware("http")
async def instrument_requests(request, call_next):
    """Instrumenta requisições HTTP com métricas Prometheus."""
    method = request.method
    endpoint = request.url.path
    
    # Incrementar contador de requisições
    api_requests_total.labels(method=method, endpoint=endpoint, status="started").inc()
    
    # Medir tempo de resposta
    start_time = time.time()
    try:
        response = await call_next(request)
        status = response.status_code
    except Exception as e:
        status = 500
        raise
    finally:
        duration = time.time() - start_time
        api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    
    return response

# Iniciar servidor de métricas
start_http_server(9090)
```

#### Dashboards Grafana

O GEIH utiliza dashboards Grafana para visualização de métricas em tempo real:

1. **Dashboard de Visão Geral do Sistema**:
   - Saúde geral dos serviços
   - Utilização de recursos (CPU, memória, disco)
   - Taxa de requisições e erros

2. **Dashboard de API**:
   - Latência de endpoints
   - Taxa de requisições por endpoint
   - Códigos de status HTTP
   - Usuários ativos

3. **Dashboard de Pipeline de Dados**:
   - Status de jobs de ingestão
   - Volume de dados processados
   - Tempo de processamento
   - Taxa de sucesso/falha

4. **Dashboard de Modelos de ML**:
   - Desempenho de modelos
   - Latência de predição
   - Drift de dados
   - Utilização de recursos

### Rastreamento Distribuído

O GEIH utiliza OpenTelemetry para rastreamento distribuído de requisições e operações:

```python
# Exemplo conceitual de rastreamento distribuído
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configurar provedor de tracer
resource = Resource(attributes={
    SERVICE_NAME: "geih-api"
})

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# Uso em funções
async def process_environmental_data(data_source, region, date_range):
    """Processa dados ambientais com rastreamento."""
    with tracer.start_as_current_span("process_environmental_data") as span:
        # Adicionar atributos ao span
        span.set_attribute("data_source", data_source)
        span.set_attribute("region", region)
        span.set_attribute("date_range", str(date_range))
        
        # Obter dados
        with tracer.start_as_current_span("fetch_data"):
            raw_data = await fetch_data(data_source, region, date_range)
            span.set_attribute("data_size", len(raw_data))
        
        # Processar dados
        with tracer.start_as_current_span("transform_data"):
            processed_data = transform_data(raw_data)
        
        # Persistir dados
        with tracer.start_as_current_span("persist_data"):
            result = await persist_data(processed_data)
        
        return result
```

### Alertas e Notificações

O GEIH implementa alertas baseados em regras para notificar a equipe sobre problemas:

#### Configuração de Alertas no Prometheus

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'team-email'
  routes:
    - match:
        severity: critical
      receiver: 'team-pager'
      repeat_interval: 1h

receivers:
  - name: 'team-email'
    email_configs:
      - to: 'team@geih.org'
        from: 'alerts@geih.org'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alerts@geih.org'
        auth_password: '{{ .EmailPassword }}'
        send_resolved: true
  
  - name: 'team-pager'
    webhook_configs:
      - url: 'https://pager.example.com/webhook'
        send_resolved: true
```

#### Regras de Alerta

```yaml
# alert_rules.yml
groups:
  - name: geih-alerts
    rules:
      - alert: HighErrorRate
        expr: sum(rate(api_requests_total{status=~"5.."}[5m])) / sum(rate(api_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Alta taxa de erros na API"
          description: "A taxa de erros está acima de 5% nos últimos 5 minutos"
      
      - alert: SlowAPIResponse
        expr: histogram_quantile(0.95, sum(rate(api_request_duration_seconds_bucket[5m])) by (le, endpoint)) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Resposta lenta da API"
          description: "O percentil 95 do tempo de resposta está acima de 1 segundo para o endpoint {{ $labels.endpoint }}"
      
      - alert: DataPipelineFailure
        expr: sum(rate(data_pipeline_job_status{status="failed"}[15m])) > 0
        for: 15m
        labels:
          severity: critical
        annotations:
          summary: "Falha no pipeline de dados"
          description: "Jobs do pipeline de dados estão falhando nos últimos 15 minutos"
      
      - alert: ModelDriftDetected
        expr: model_drift_detected > 0
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Drift detectado no modelo"
          description: "Drift de dados detectado no modelo {{ $labels.model_name }}"
```

### Health Checks e Readiness Probes

O GEIH implementa health checks para monitorar a saúde dos serviços:

```python
# Exemplo conceitual de health checks
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class HealthStatus(BaseModel):
    status: str
    version: str
    components: dict

async def check_database():
    """Verifica conexão com banco de dados."""
    try:
        # Verificar conexão com banco de dados
        await database.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_data_lake():
    """Verifica conexão com data lake."""
    try:
        # Verificar conexão com data lake
        client = get_minio_client()
        client.list_buckets()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Endpoint de health check."""
    db_status = await check_database()
    data_lake_status = await check_data_lake()
    
    components = {
        "database": db_status,
        "data_lake": data_lake_status,
        # Outros componentes
    }
    
    # Verificar se todos os componentes estão saudáveis
    overall_status = "healthy"
    for component, status in components.items():
        if status["status"] != "healthy":
            overall_status = "degraded"
            if component in ["database", "data_lake"]:  # Componentes críticos
                overall_status = "unhealthy"
                break
    
    return HealthStatus(
        status=overall_status,
        version="1.0.0",
        components=components
    )

@app.get("/readiness")
async def readiness_check():
    """Endpoint de readiness check."""
    # Verificar se o serviço está pronto para receber tráfego
    if not is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not ready"
        )
    return {"status": "ready"}
```

## Segurança

O GEIH implementa múltiplas camadas de segurança para proteger dados, APIs e infraestrutura:

### Autenticação e Autorização

#### OAuth2 com JWT

```python
# Exemplo conceitual de autenticação OAuth2 com JWT
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Configuração
SECRET_KEY = "sua-chave-secreta-aqui"  # Em produção, usar variável de ambiente
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Modelos
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: list[str] = []

# Utilitários
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

#### Controle de Acesso Baseado em Papéis (RBAC)

```python
# Exemplo conceitual de RBAC
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import BaseModel, ValidationError
from jose import jwt

# Definição de escopos/papéis
class RoleScope:
    READ_DATA = "data:read"
    WRITE_DATA = "data:write"
    ADMIN = "admin"
    ALERT_MANAGE = "alert:manage"
    MODEL_TRAIN = "model:train"
    MODEL_DEPLOY = "model:deploy"

# Verificação de permissões
def has_permission(required_scopes: list[str], user_scopes: list[str]) -> bool:
    """Verifica se o usuário tem as permissões necessárias."""
    # Admin tem acesso a tudo
    if RoleScope.ADMIN in user_scopes:
        return True
    
    # Verificar se o usuário tem todos os escopos necessários
    return all(scope in user_scopes for scope in required_scopes)

# Dependência para verificar permissões
async def verify_scopes(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
):
    """Verifica se o token tem os escopos necessários."""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Verificar se o usuário tem os escopos necessários
    if not has_permission(security_scopes.scopes, token_scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )
    
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    
    return user

# Uso em endpoints
@app.get("/data/{data_id}", tags=["data"])
async def read_data(
    data_id: str,
    user: User = Security(verify_scopes, scopes=[RoleScope.READ_DATA])
):
    """Endpoint para leitura de dados."""
    return {"data_id": data_id, "content": "Dados ambientais"}

@app.post("/data", tags=["data"])
async def create_data(
    data: dict,
    user: User = Security(verify_scopes, scopes=[RoleScope.WRITE_DATA])
):
    """Endpoint para criação de dados."""
    return {"status": "created", "data_id": "123"}

@app.post("/models/deploy/{model_id}", tags=["models"])
async def deploy_model(
    model_id: str,
    user: User = Security(verify_scopes, scopes=[RoleScope.MODEL_DEPLOY])
):
    """Endpoint para implantação de modelo."""
    return {"status": "deployed", "model_id": model_id}
```

### Segurança de Dados

#### Criptografia em Trânsito

O GEIH utiliza HTTPS/TLS para todas as comunicações externas:

```python
# Exemplo conceitual de configuração HTTPS com FastAPI e Uvicorn
import uvicorn
from fastapi import FastAPI

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="/path/to/key.pem",
        ssl_certfile="/path/to/cert.pem"
    )
```

#### Criptografia em Repouso

O GEIH implementa criptografia para dados sensíveis armazenados:

```python
# Exemplo conceitual de criptografia de dados sensíveis
from cryptography.fernet import Fernet
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class DataEncryption:
    """Utilitário para criptografia de dados sensíveis."""
    
    def __init__(self, key=None):
        """Inicializa com chave existente ou gera nova."""
        if key:
            self.key = key
        else:
            self.key = self._generate_key()
        self.cipher = Fernet(self.key)
    
    def _generate_key(self):
        """Gera chave de criptografia."""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(os.environ.get("ENCRYPTION_PASSWORD", "default").encode()))
        return key
    
    def encrypt(self, data):
        """Criptografa dados."""
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data):
        """Descriptografa dados."""
        return self.cipher.decrypt(encrypted_data)

# Uso para criptografia de credenciais de API
def store_api_credentials(service_name, credentials):
    """Armazena credenciais de API de forma segura."""
    encryption = DataEncryption()
    encrypted_credentials = encryption.encrypt(json.dumps(credentials).encode())
    
    # Armazenar credenciais criptografadas
    with open(f"/path/to/credentials/{service_name}.enc", "wb") as f:
        f.write(encrypted_credentials)
    
    # Armazenar chave de forma segura (em ambiente de produção, usar cofre de senhas)
    with open(f"/path/to/keys/{service_name}.key", "wb") as f:
        f.write(encryption.key)

def get_api_credentials(service_name):
    """Recupera credenciais de API."""
    # Carregar chave
    with open(f"/path/to/keys/{service_name}.key", "rb") as f:
        key = f.read()
    
    # Carregar credenciais criptografadas
    with open(f"/path/to/credentials/{service_name}.enc", "rb") as f:
        encrypted_credentials = f.read()
    
    # Descriptografar
    encryption = DataEncryption(key=key)
    credentials = json.loads(encryption.decrypt(encrypted_credentials))
    
    return credentials
```

#### Mascaramento de Dados Sensíveis

```python
# Exemplo conceitual de mascaramento de dados sensíveis em logs
import re
from loguru import logger

def mask_sensitive_data(record):
    """Mascara dados sensíveis em logs."""
    # Lista de padrões a serem mascarados
    patterns = [
        (r"password[\"']?\s*:\s*[\"']([^\"']+)[\"']", r"password\": \"*****\""),
        (r"api_key[\"']?\s*:\s*[\"']([^\"']+)[\"']", r"api_key\": \"*****\""),
        (r"token[\"']?\s*:\s*[\"']([^\"']+)[\"']", r"token\": \"*****\""),
        (r"secret[\"']?\s*:\s*[\"']([^\"']+)[\"']", r"secret\": \"*****\""),
        (r"(\d{3})-(\d{2})-(\d{4})", r"***-**-****"),  # CPF
        (r"(\d{4})-?(\d{4})-?(\d{4})-?(\d{4})", r"****-****-****-****")  # Cartão de crédito
    ]
    
    # Aplicar mascaramento
    message = record["message"]
    for pattern, replacement in patterns:
        message = re.sub(pattern, replacement, message)
    
    record["message"] = message
    return record

# Configurar logger com mascaramento
logger.configure(patcher=mask_sensitive_data)
```

### Proteção contra Ameaças Comuns

#### Proteção contra Injeção de SQL

```python
# Exemplo conceitual de proteção contra injeção de SQL
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

async def safe_query(session: AsyncSession, table: str, filters: dict):
    """Executa consulta SQL de forma segura."""
    # Construir consulta parametrizada
    query = f"SELECT * FROM {table} WHERE "
    conditions = []
    params = {}
    
    for key, value in filters.items():
        conditions.append(f"{key} = :{key}")
        params[key] = value
    
    query += " AND ".join(conditions)
    
    # Executar consulta parametrizada
    result = await session.execute(text(query), params)
    return result.fetchall()

# Uso com SQLAlchemy ORM
async def get_hotspots(session: AsyncSession, region: str, start_date: str, end_date: str):
    """Obtém focos de calor de forma segura."""
    query = select(Hotspot).where(
        Hotspot.region == region,
        Hotspot.date >= start_date,
        Hotspot.date <= end_date
    )
    result = await session.execute(query)
    return result.scalars().all()
```

#### Proteção contra XSS

```python
# Exemplo conceitual de proteção contra XSS
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import bleach

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def sanitize_html(html_content):
    """Sanitiza conteúdo HTML para prevenir XSS."""
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'img']
    allowed_attrs = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
    }
    return bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

@app.get("/report/{report_id}", response_class=HTMLResponse)
async def get_report(request: Request, report_id: str):
    """Endpoint para exibição de relatório."""
    # Obter conteúdo do relatório
    report_content = get_report_content(report_id)
    
    # Sanitizar conteúdo
    sanitized_content = sanitize_html(report_content)
    
    # Renderizar template
    return templates.TemplateResponse(
        "report.html",
        {"request": request, "content": sanitized_content}
    )
```

#### Proteção contra CSRF

```python
# Exemplo conceitual de proteção contra CSRF
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import APIKeyCookie
from starlette.middleware.sessions import SessionMiddleware
import secrets

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="sua-chave-secreta-aqui")

csrf_cookie = APIKeyCookie(name="csrf_token", auto_error=False)

def generate_csrf_token():
    """Gera token CSRF."""
    return secrets.token_hex(32)

async def verify_csrf_token(
    request: Request,
    csrf_token: str = Depends(csrf_cookie)
):
    """Verifica token CSRF."""
    # Obter token da sessão
    session_token = request.session.get("csrf_token")
    
    # Verificar se token existe e corresponde
    if not session_token or not csrf_token or session_token != csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token invalid"
        )
    
    return csrf_token

@app.get("/csrf-token")
async def get_csrf_token(request: Request):
    """Endpoint para obter token CSRF."""
    token = generate_csrf_token()
    request.session["csrf_token"] = token
    return {"csrf_token": token}

@app.post("/api/data", dependencies=[Depends(verify_csrf_token)])
async def create_data(data: dict):
    """Endpoint protegido contra CSRF."""
    return {"status": "created", "data": data}
```

#### Rate Limiting

```python
# Exemplo conceitual de rate limiting
from fastapi import FastAPI, Depends, HTTPException, Request, status
import time
import redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

app = FastAPI()

@app.on_event("startup")
async def startup():
    """Inicializa limitador de taxa."""
    redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    await FastAPILimiter.init(redis_client)

# Limitar a 10 requisições por minuto
@app.get("/api/public-data", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_public_data():
    """Endpoint público com rate limiting."""
    return {"data": "Dados públicos"}

# Limitar a 100 requisições por minuto para usuários autenticados
@app.get("/api/user-data")
async def get_user_data(
    current_user: User = Depends(get_current_user),
    _: None = Depends(RateLimiter(times=100, seconds=60))
):
    """Endpoint para usuários autenticados com rate limiting."""
    return {"data": "Dados do usuário", "user": current_user.username}

# Rate limiting personalizado por IP
class IPRateLimiter:
    """Limitador de taxa baseado em IP."""
    
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds
    
    async def __call__(self, request: Request):
        """Verifica limite de taxa para o IP."""
        ip = request.client.host
        redis_client = FastAPILimiter.redis
        key = f"rate_limit:{ip}"
        
        # Verificar contagem atual
        current = await redis_client.get(key)
        if current is None:
            # Primeira requisição
            await redis_client.set(key, 1, ex=self.seconds)
        elif int(current) >= self.times:
            # Limite excedido
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        else:
            # Incrementar contagem
            await redis_client.incr(key)
        
        return True

# Uso do limitador personalizado
@app.get("/api/public-map", dependencies=[Depends(IPRateLimiter(times=5, seconds=60))])
async def get_public_map():
    """Endpoint para mapa público com rate limiting por IP."""
    return {"map_data": "Dados do mapa público"}
```

### Conformidade com Padrões

#### LGPD (Lei Geral de Proteção de Dados)

O GEIH implementa medidas para conformidade com a LGPD:

1. **Consentimento**:
   - Obtenção e registro de consentimento para coleta e uso de dados pessoais
   - Interface para gerenciamento de consentimento

2. **Minimização de Dados**:
   - Coleta apenas de dados necessários para a finalidade declarada
   - Anonimização de dados quando possível

3. **Direitos do Titular**:
   - Implementação de APIs para acesso, correção e exclusão de dados pessoais
   - Mecanismos para portabilidade de dados

4. **Segurança**:
   - Medidas técnicas e administrativas para proteção de dados
   - Registro de atividades de processamento

5. **Notificação de Incidentes**:
   - Procedimentos para detecção e notificação de violações de dados
   - Plano de resposta a incidentes

```python
# Exemplo conceitual de API para direitos do titular
@app.get("/api/user/data", tags=["user"])
async def get_user_data(current_user: User = Depends(get_current_active_user)):
    """Endpoint para acesso aos dados do usuário (LGPD Art. 18, II)."""
    user_data = await get_all_user_data(current_user.id)
    return user_data

@app.put("/api/user/data", tags=["user"])
async def update_user_data(
    data: UserUpdateData,
    current_user: User = Depends(get_current_active_user)
):
    """Endpoint para correção de dados do usuário (LGPD Art. 18, III)."""
    updated_data = await update_user_data_in_db(current_user.id, data)
    return updated_data

@app.delete("/api/user/data", tags=["user"])
async def delete_user_data(current_user: User = Depends(get_current_active_user)):
    """Endpoint para exclusão de dados do usuário (LGPD Art. 18, VI)."""
    await anonymize_user_data(current_user.id)
    return {"status": "success", "message": "Dados anonimizados com sucesso"}

@app.get("/api/user/data/export", tags=["user"])
async def export_user_data(current_user: User = Depends(get_current_active_user)):
    """Endpoint para portabilidade de dados do usuário (LGPD Art. 18, V)."""
    user_data = await get_all_user_data(current_user.id)
    return JSONResponse(
        content=user_data,
        headers={"Content-Disposition": f"attachment; filename=user_data_{current_user.id}.json"}
    )
```

#### Princípios FAIR para Dados Abertos

O GEIH adota os princípios FAIR (Findable, Accessible, Interoperable, Reusable) para dados abertos:

1. **Findable (Encontrável)**:
   - Atribuição de identificadores persistentes (DOI, URI)
   - Metadados ricos e indexáveis
   - Registro em catálogos de dados

2. **Accessible (Acessível)**:
   - Protocolos padronizados e abertos (HTTP, REST)
   - Autenticação e autorização quando necessário
   - Metadados acessíveis mesmo quando os dados não estão

3. **Interoperable (Interoperável)**:
   - Formatos de dados padronizados (GeoJSON, CSV, NetCDF)
   - Vocabulários e ontologias compartilhados
   - Referências a outros dados

4. **Reusable (Reutilizável)**:
   - Licenças claras e abertas
   - Proveniência detalhada
   - Padrões da comunidade

```python
# Exemplo conceitual de API para dados abertos seguindo princípios FAIR
@app.get("/api/open-data/catalog", tags=["open-data"])
async def get_data_catalog():
    """Endpoint para catálogo de dados abertos (FAIR - Findable)."""
    catalog = await get_open_data_catalog()
    return catalog

@app.get("/api/open-data/{dataset_id}", tags=["open-data"])
async def get_dataset(
    dataset_id: str,
    format: str = Query("json", enum=["json", "geojson", "csv", "netcdf"])
):
    """Endpoint para acesso a conjunto de dados (FAIR - Accessible)."""
    dataset = await get_open_dataset(dataset_id, format)
    
    # Adicionar cabeçalhos para FAIR
    headers = {
        "Access-Control-Allow-Origin": "*",
        "X-Dataset-License": "CC-BY-4.0",
        "X-Dataset-Version": "1.0.0",
        "X-Dataset-DOI": f"10.5281/zenodo.{dataset_id}",
        "X-Dataset-Citation": f"GEIH (2025). Environmental dataset {dataset_id}. Zenodo. 10.5281/zenodo.{dataset_id}"
    }
    
    # Retornar dados no formato solicitado
    if format == "json":
        return JSONResponse(content=dataset, headers=headers)
    elif format == "geojson":
        return JSONResponse(content=dataset, headers=headers)
    elif format == "csv":
        return Response(
            content=convert_to_csv(dataset),
            media_type="text/csv",
            headers={**headers, "Content-Disposition": f"attachment; filename=dataset_{dataset_id}.csv"}
        )
    elif format == "netcdf":
        return Response(
            content=convert_to_netcdf(dataset),
            media_type="application/x-netcdf",
            headers={**headers, "Content-Disposition": f"attachment; filename=dataset_{dataset_id}.nc"}
        )

@app.get("/api/open-data/{dataset_id}/metadata", tags=["open-data"])
async def get_dataset_metadata(dataset_id: str):
    """Endpoint para metadados de conjunto de dados (FAIR - Findable, Reusable)."""
    metadata = await get_open_dataset_metadata(dataset_id)
    return metadata
```

## Diagrama de Arquitetura de Observabilidade e Segurança

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Camada de Aplicação                               │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │  API     │   │ Pipeline │   │ Serviço  │   │ Serviço  │   │ Serviço  ││
│  │  REST    │   │ de Dados │   │   ML     │   │de Alertas│   │   ...    ││
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘│
└───────┼──────────────┼──────────────┼──────────────┼──────────────┼──────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Observabilidade                                   │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │ Logging  │   │ Métricas │   │Rastreamen.│  │ Health   │   │ Alertas  ││
│  │(Loguru)  │   │(Promethe)│   │(OpenTelem)│  │ Checks   │   │          ││
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘│
└───────┼──────────────┼──────────────┼──────────────┼──────────────┼──────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Visualização e Monitoramento                      │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │ Grafana  │   │ Jaeger   │   │AlertManag.│  │ Kibana   │   │ Prometheus││
│  │Dashboards│   │  UI      │   │          │  │          │   │          ││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘│
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        Segurança                                         │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │Autenticaç│   │Autorizaç.│   │Criptograf│   │Proteção  │   │Conformida││
│  │(OAuth/JWT)│   │ (RBAC)   │   │          │  │Ameaças   │   │(LGPD/FAIR)││
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘│
└───────┼──────────────┼──────────────┼──────────────┼──────────────┼──────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Infraestrutura                                    │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │  HTTPS/  │   │ Firewalls│   │  Backup  │   │Segregação│   │Atualizaç.││
│  │   TLS    │   │          │   │          │  │  de Rede  │   │Automática││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

## Implementação Prática

### Configuração do Docker Compose para Observabilidade

```yaml
# docker-compose.observability.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.37.0
    volumes:
      - ./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    ports:
      - "9090:9090"
    networks:
      - geih-network

  grafana:
    image: grafana/grafana:9.0.0
    volumes:
      - ./infra/grafana/provisioning:/etc/grafana/provisioning
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3000:3000"
    networks:
      - geih-network
    depends_on:
      - prometheus

  alertmanager:
    image: prom/alertmanager:v0.24.0
    volumes:
      - ./infra/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    networks:
      - geih-network
    depends_on:
      - prometheus

  jaeger:
    image: jaegertracing/all-in-one:1.35
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    networks:
      - geih-network

  node-exporter:
    image: prom/node-exporter:v1.3.1
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    networks:
      - geih-network

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:v0.10.0
    environment:
      - DATA_SOURCE_NAME=postgresql://postgres:postgres@postgres:5432/geih?sslmode=disable
    ports:
      - "9187:9187"
    networks:
      - geih-network
    depends_on:
      - postgres

volumes:
  prometheus_data:
  grafana_data:

networks:
  geih-network:
    driver: bridge
```

### Configuração do Docker Compose para Segurança

```yaml
# docker-compose.security.yml
version: '3.8'

services:
  traefik:
    image: traefik:v2.6
    command:
      - "--api.insecure=false"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=admin@geih.org"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./infra/traefik/letsencrypt:/letsencrypt
    networks:
      - geih-network

  redis:
    image: redis:6.2-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - geih-network

  vault:
    image: vault:1.10.3
    cap_add:
      - IPC_LOCK
    volumes:
      - ./infra/vault/config:/vault/config
      - vault_data:/vault/data
    environment:
      - VAULT_ADDR=http://0.0.0.0:8200
      - VAULT_API_ADDR=http://0.0.0.0:8200
    command: server -config=/vault/config/vault.hcl
    networks:
      - geih-network

volumes:
  redis_data:
  vault_data:

networks:
  geih-network:
    driver: bridge
```

## Próximos Passos

1. **Implementação da Infraestrutura Base**: Setup de Prometheus, Grafana, Loguru e OpenTelemetry
2. **Configuração de Segurança**: Implementação de OAuth2/JWT, RBAC e proteções contra ameaças comuns
3. **Integração com CI/CD**: Automação de testes de segurança e verificações de conformidade
4. **Documentação de Políticas**: Elaboração de políticas de segurança e privacidade
5. **Treinamento da Equipe**: Capacitação em práticas de segurança e observabilidade

Este documento de políticas de observabilidade e segurança foi projetado para atender aos requisitos do GEIH, garantindo monitoramento eficaz, logging estruturado, segurança robusta e conformidade com padrões relevantes como LGPD e FAIR.
