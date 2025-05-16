# Fluxo de MLOps e Experimentos do GEIH

Este documento detalha o fluxo de MLOps e experimentos do Global Environmental Intelligence Hub (GEIH), descrevendo a estrutura para desenvolvimento, treinamento, avaliação e implantação de modelos de IA para análise preditiva ambiental.

## Visão Geral do Fluxo de MLOps

O GEIH implementa um fluxo de MLOps leve e modular, focado em replicabilidade e experimentação estruturada, preparando o caminho para a futura integração de modelos avançados como FourCastNet e NVIDIA Modulus:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Preparação  │ -> │Experimentação│ -> │  Avaliação  │ -> │Versionamento│ -> │ Implantação │
│  de Dados   │    │  e Treino   │    │  de Modelos │    │  de Modelos │    │  de Modelos │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Estrutura de Diretórios para MLOps

```
ai_models/
├── data/                      # Dados para treinamento e avaliação
│   ├── raw/                   # Dados brutos
│   ├── processed/             # Dados processados para ML
│   ├── features/              # Features extraídas
│   └── external/              # Dados externos de referência
│
├── experiments/               # Experimentos de ML
│   ├── fire_risk/             # Experimentos para risco de incêndio
│   ├── deforestation/         # Experimentos para detecção de desmatamento
│   └── climate_prediction/    # Experimentos para previsão climática
│
├── models/                    # Modelos treinados
│   ├── fire_risk/             # Modelos de risco de incêndio
│   ├── deforestation/         # Modelos de detecção de desmatamento
│   └── climate_prediction/    # Modelos de previsão climática
│
├── notebooks/                 # Jupyter notebooks para exploração e prototipagem
│   ├── exploratory/           # Análise exploratória de dados
│   ├── feature_engineering/   # Engenharia de features
│   └── model_evaluation/      # Avaliação de modelos
│
├── src/                       # Código-fonte para modelos e pipelines
│   ├── data/                  # Processamento de dados para ML
│   │   ├── make_dataset.py    # Scripts para criação de datasets
│   │   └── preprocess.py      # Pré-processamento de dados
│   │
│   ├── features/              # Engenharia de features
│   │   ├── build_features.py  # Construção de features
│   │   └── transformers.py    # Transformadores de features
│   │
│   ├── models/                # Implementação de modelos
│   │   ├── train_model.py     # Treinamento de modelos
│   │   ├── predict_model.py   # Predição com modelos
│   │   └── evaluate_model.py  # Avaliação de modelos
│   │
│   └── visualization/         # Visualização de resultados
│       └── visualize.py       # Funções de visualização
│
├── tests/                     # Testes automatizados
│   ├── test_data.py           # Testes para processamento de dados
│   ├── test_features.py       # Testes para engenharia de features
│   └── test_models.py         # Testes para modelos
│
├── configs/                   # Configurações para experimentos
│   ├── fire_risk_config.yaml  # Configuração para modelos de risco de incêndio
│   └── ...
│
└── mlflow/                    # Artefatos e logs do MLflow
    └── mlruns/                # Registros de experimentos
```

## Versionamento de Dados e Modelos

O GEIH utiliza DVC (Data Version Control) para versionamento de dados e modelos, garantindo reprodutibilidade e rastreabilidade:

### Estrutura de Versionamento

```
.dvc/                          # Configuração do DVC
├── config                     # Configuração global
└── .gitignore                 # Arquivos ignorados pelo Git

data.dvc                       # Metadados de versionamento de dados
models.dvc                     # Metadados de versionamento de modelos
```

### Exemplo de Configuração DVC

```yaml
# .dvc/config
['remote "s3"']
    url = s3://geih-datalake/dvc
    endpointurl = http://minio:9000
['remote "local"']
    url = /path/to/dvc-storage
```

### Fluxo de Trabalho com DVC

```bash
# Adicionar dados ao versionamento
dvc add ai_models/data/processed/fire_risk_dataset_v1.parquet

# Adicionar modelo ao versionamento
dvc add ai_models/models/fire_risk/random_forest_v1.pkl

# Enviar para armazenamento remoto
dvc push -r s3

# Recuperar versão específica
dvc checkout fire_risk_experiment_v2
dvc pull
```

## Rastreamento de Experimentos com MLflow

O GEIH utiliza MLflow para rastreamento de experimentos, métricas e artefatos:

### Estrutura de Experimentos

```
mlflow/
├── mlruns/
│   ├── 0/                     # Experimento padrão
│   ├── 1/                     # Experimento de risco de incêndio
│   │   ├── run_id_1/          # Execução específica
│   │   │   ├── metrics/       # Métricas registradas
│   │   │   ├── params/        # Parâmetros do modelo
│   │   │   └── artifacts/     # Artefatos (modelos, gráficos)
│   │   └── ...
│   └── ...
└── models/                    # Modelos registrados
    ├── fire_risk_model/       # Modelo específico
    │   ├── version_1/         # Versão do modelo
    │   └── ...
    └── ...
```

### Exemplo de Código para MLflow

```python
# Exemplo conceitual de uso do MLflow para experimentos
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Definir experimento
mlflow.set_experiment("fire_risk_prediction")

# Parâmetros do modelo
params = {
    "n_estimators": 100,
    "max_depth": 10,
    "min_samples_split": 5,
    "random_state": 42
}

# Iniciar execução do MLflow
with mlflow.start_run(run_name="random_forest_baseline"):
    # Registrar parâmetros
    mlflow.log_params(params)
    
    # Registrar tags
    mlflow.set_tags({
        "region": "amazon",
        "data_version": "v1.0",
        "model_type": "random_forest"
    })
    
    # Treinar modelo
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    
    # Fazer predições
    y_pred = model.predict(X_test)
    
    # Calcular métricas
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average="weighted"),
        "recall": recall_score(y_test, y_pred, average="weighted"),
        "f1": f1_score(y_test, y_pred, average="weighted")
    }
    
    # Registrar métricas
    for metric_name, metric_value in metrics.items():
        mlflow.log_metric(metric_name, metric_value)
    
    # Registrar modelo
    mlflow.sklearn.log_model(model, "model")
    
    # Registrar artefatos (gráficos, relatórios)
    mlflow.log_artifact("path/to/confusion_matrix.png")
    mlflow.log_artifact("path/to/feature_importance.png")
    
    # Registrar modelo no registro de modelos
    mlflow.register_model(
        "runs:/{}/model".format(mlflow.active_run().info.run_id),
        "fire_risk_model"
    )
```

## Modelos Iniciais e Casos de Uso

O GEIH implementará inicialmente modelos mais simples e interpretáveis, preparando a infraestrutura para modelos mais complexos no futuro:

### 1. Modelo de Risco de Incêndio

**Objetivo**: Prever áreas com alto risco de incêndio na Amazônia Legal.

**Abordagem Inicial**:
- Modelo: Random Forest ou Gradient Boosting
- Features: Dados históricos de focos de calor, precipitação, temperatura, umidade, tipo de vegetação, proximidade a estradas e assentamentos
- Saída: Mapa de risco categorizado (baixo, médio, alto, crítico)

**Preparação para Modelos Avançados**:
- Estrutura para integração futura com FourCastNet para previsões climáticas de alta resolução
- Interfaces para modelos baseados em física como NVIDIA Modulus

### 2. Detecção de Desmatamento

**Objetivo**: Identificar áreas de desmatamento recente e prever tendências.

**Abordagem Inicial**:
- Modelo: Classificação supervisionada com XGBoost ou LightGBM
- Features: Séries temporais de índices de vegetação (NDVI, EVI), dados de precipitação, proximidade a áreas previamente desmatadas
- Saída: Classificação binária (desmatamento/não-desmatamento) com probabilidades

**Preparação para Modelos Avançados**:
- Estrutura para integração futura com modelos de deep learning para análise de imagens de satélite
- Interfaces para modelos de séries temporais complexos

## Fluxo de Desenvolvimento de Modelos

### 1. Preparação de Dados

```python
# Exemplo conceitual de preparação de dados
import pandas as pd
import geopandas as gpd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def prepare_fire_risk_dataset(hotspots_path, climate_path, landcover_path, output_path):
    """Prepara dataset para modelo de risco de incêndio."""
    # Carregar dados
    hotspots = gpd.read_file(hotspots_path)
    climate = pd.read_csv(climate_path)
    landcover = gpd.read_file(landcover_path)
    
    # Processamento geoespacial
    # - Agregação de pontos de focos por grade
    # - Junção espacial com dados climáticos e cobertura do solo
    # - Cálculo de features derivadas (distância a estradas, etc.)
    
    # Divisão em treino/teste
    X = dataset.drop(columns=["fire_occurred"])
    y = dataset["fire_occurred"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Normalização
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Salvar dados processados
    pd.to_parquet(
        pd.DataFrame(X_train_scaled, columns=X.columns),
        output_path + "/X_train.parquet"
    )
    pd.to_parquet(
        pd.DataFrame(X_test_scaled, columns=X.columns),
        output_path + "/X_test.parquet"
    )
    pd.to_parquet(
        pd.DataFrame(y_train, columns=["target"]),
        output_path + "/y_train.parquet"
    )
    pd.to_parquet(
        pd.DataFrame(y_test, columns=["target"]),
        output_path + "/y_test.parquet"
    )
    
    # Salvar metadados
    with open(output_path + "/metadata.json", "w") as f:
        json.dump({
            "features": list(X.columns),
            "target": "fire_occurred",
            "scaler": "StandardScaler",
            "train_size": len(X_train),
            "test_size": len(X_test),
            "positive_class_ratio": y.mean(),
            "creation_date": datetime.now().isoformat()
        }, f)
```

### 2. Experimentação e Treinamento

```python
# Exemplo conceitual de experimentação com diferentes modelos
import mlflow
import yaml
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def train_and_evaluate_models(config_path, data_path):
    """Treina e avalia múltiplos modelos para risco de incêndio."""
    # Carregar configuração
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Carregar dados
    X_train = pd.read_parquet(data_path + "/X_train.parquet")
    X_test = pd.read_parquet(data_path + "/X_test.parquet")
    y_train = pd.read_parquet(data_path + "/y_train.parquet")["target"]
    y_test = pd.read_parquet(data_path + "/y_test.parquet")["target"]
    
    # Definir experimento MLflow
    mlflow.set_experiment(config["experiment_name"])
    
    # Iterar sobre modelos na configuração
    for model_config in config["models"]:
        model_name = model_config["name"]
        model_params = model_config["params"]
        
        # Selecionar modelo
        if model_name == "random_forest":
            model = RandomForestClassifier(**model_params)
        elif model_name == "gradient_boosting":
            model = GradientBoostingClassifier(**model_params)
        elif model_name == "logistic_regression":
            model = LogisticRegression(**model_params)
        else:
            raise ValueError(f"Modelo não suportado: {model_name}")
        
        # Iniciar execução do MLflow
        with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Registrar parâmetros
            mlflow.log_params(model_params)
            
            # Treinar modelo
            model.fit(X_train, y_train)
            
            # Fazer predições
            y_pred = model.predict(X_test)
            
            # Calcular métricas
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, average="weighted"),
                "recall": recall_score(y_test, y_pred, average="weighted"),
                "f1": f1_score(y_test, y_pred, average="weighted")
            }
            
            # Registrar métricas
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Registrar modelo
            mlflow.sklearn.log_model(model, "model")
            
            # Gerar e registrar visualizações
            plot_confusion_matrix(y_test, y_pred, "confusion_matrix.png")
            mlflow.log_artifact("confusion_matrix.png")
            
            if hasattr(model, "feature_importances_"):
                plot_feature_importance(model, X_train.columns, "feature_importance.png")
                mlflow.log_artifact("feature_importance.png")
```

### 3. Avaliação de Modelos

```python
# Exemplo conceitual de avaliação de modelos
import mlflow
from mlflow.tracking import MlflowClient
from sklearn.metrics import roc_curve, precision_recall_curve, average_precision_score

def evaluate_best_model(experiment_name, metric="f1", min_version=None):
    """Avalia o melhor modelo com base na métrica especificada."""
    client = MlflowClient()
    
    # Obter ID do experimento
    experiment = client.get_experiment_by_name(experiment_name)
    experiment_id = experiment.experiment_id
    
    # Buscar execuções do experimento
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        filter_string=f"metrics.{metric} > 0",
        order_by=[f"metrics.{metric} DESC"]
    )
    
    if not runs:
        raise ValueError(f"Nenhuma execução encontrada para o experimento {experiment_name}")
    
    # Selecionar melhor execução
    best_run = runs[0]
    best_run_id = best_run.info.run_id
    best_metric_value = best_run.data.metrics[metric]
    
    print(f"Melhor modelo: {best_run.data.tags.get('mlflow.runName', 'N/A')}")
    print(f"Métrica {metric}: {best_metric_value:.4f}")
    
    # Carregar melhor modelo
    best_model = mlflow.sklearn.load_model(f"runs:/{best_run_id}/model")
    
    # Carregar dados de teste
    X_test = pd.read_parquet("path/to/data/X_test.parquet")
    y_test = pd.read_parquet("path/to/data/y_test.parquet")["target"]
    
    # Avaliação detalhada
    y_pred = best_model.predict(X_test)
    y_prob = best_model.predict_proba(X_test)[:, 1]
    
    # Curva ROC
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    
    # Curva Precision-Recall
    precision, recall, _ = precision_recall_curve(y_test, y_prob)
    avg_precision = average_precision_score(y_test, y_prob)
    
    # Registrar avaliação detalhada
    with mlflow.start_run(run_id=best_run_id):
        # Registrar métricas adicionais
        mlflow.log_metric("roc_auc", roc_auc)
        mlflow.log_metric("avg_precision", avg_precision)
        
        # Gerar e registrar visualizações adicionais
        plot_roc_curve(fpr, tpr, roc_auc, "roc_curve.png")
        mlflow.log_artifact("roc_curve.png")
        
        plot_precision_recall_curve(precision, recall, avg_precision, "pr_curve.png")
        mlflow.log_artifact("pr_curve.png")
        
        # Registrar modelo no registro de modelos
        model_name = f"{experiment_name.lower().replace(' ', '_')}_model"
        model_version = mlflow.register_model(
            f"runs:/{best_run_id}/model",
            model_name
        )
        
        return best_model, model_version.version
```

### 4. Implantação de Modelos

```python
# Exemplo conceitual de implantação de modelo
import mlflow
import joblib
import json

def deploy_model(model_name, version, deployment_path):
    """Implanta modelo para uso em produção."""
    # Carregar modelo do registro MLflow
    model = mlflow.sklearn.load_model(
        model_uri=f"models:/{model_name}/{version}"
    )
    
    # Salvar modelo em formato para produção
    joblib.dump(model, f"{deployment_path}/model.joblib")
    
    # Carregar metadados do modelo
    client = MlflowClient()
    model_version = client.get_model_version(model_name, version)
    run_id = model_version.run_id
    
    # Obter parâmetros e métricas da execução
    run = client.get_run(run_id)
    params = run.data.params
    metrics = run.data.metrics
    
    # Salvar metadados para uso em produção
    with open(f"{deployment_path}/model_info.json", "w") as f:
        json.dump({
            "name": model_name,
            "version": version,
            "run_id": run_id,
            "params": params,
            "metrics": metrics,
            "creation_date": datetime.now().isoformat(),
            "description": model_version.description
        }, f)
    
    # Criar script de predição
    with open(f"{deployment_path}/predict.py", "w") as f:
        f.write("""
import joblib
import pandas as pd
import numpy as np

def load_model():
    return joblib.load("model.joblib")

def predict(model, data):
    # Verificar se os dados estão no formato correto
    if isinstance(data, dict):
        data = pd.DataFrame([data])
    elif isinstance(data, list):
        data = pd.DataFrame(data)
    
    # Fazer predição
    predictions = model.predict(data)
    probabilities = model.predict_proba(data)[:, 1]
    
    # Retornar resultados
    results = []
    for i in range(len(predictions)):
        results.append({
            "prediction": int(predictions[i]),
            "probability": float(probabilities[i]),
            "risk_level": get_risk_level(probabilities[i])
        })
    
    return results

def get_risk_level(probability):
    if probability < 0.25:
        return "baixo"
    elif probability < 0.5:
        return "médio"
    elif probability < 0.75:
        return "alto"
    else:
        return "crítico"

if __name__ == "__main__":
    import sys
    import json
    
    # Carregar modelo
    model = load_model()
    
    # Carregar dados de entrada
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        with open(input_file) as f:
            input_data = json.load(f)
    else:
        input_data = json.loads(sys.stdin.read())
    
    # Fazer predição
    results = predict(model, input_data)
    
    # Imprimir resultados
    print(json.dumps(results, indent=2))
        """)
    
    print(f"Modelo {model_name} versão {version} implantado em {deployment_path}")
    return f"{deployment_path}/model.joblib"
```

## Integração com Modelos Avançados (Preparação Futura)

O GEIH está preparado para integração futura com modelos avançados como FourCastNet e NVIDIA Modulus:

### Adaptadores para Modelos Externos

```python
# Exemplo conceitual de adaptador para FourCastNet
class FourCastNetAdapter:
    """Adaptador para integração com modelo FourCastNet."""
    
    def __init__(self, model_path, config_path):
        self.model_path = model_path
        self.config_path = config_path
        self.model = None
    
    def load_model(self):
        """Carrega modelo FourCastNet."""
        # Implementação futura para carregar modelo FourCastNet
        pass
    
    async def predict(self, input_data):
        """Realiza predição com FourCastNet."""
        # Implementação futura para predição com FourCastNet
        pass
    
    def get_metadata(self):
        """Retorna metadados do modelo."""
        return {
            "name": "FourCastNet",
            "type": "climate_prediction",
            "description": "Modelo de previsão climática baseado em deep learning",
            "input_variables": ["temperature", "pressure", "humidity", "wind"],
            "output_variables": ["temperature_forecast", "precipitation_forecast"],
            "spatial_resolution": "0.25 degrees",
            "temporal_resolution": "6 hours",
            "forecast_horizon": "10 days"
        }
```

### Registro de Modelos Externos

```python
# Exemplo conceitual de registro de modelos externos
class ExternalModelRegistry:
    """Registro para modelos externos não gerenciados pelo MLflow."""
    
    def __init__(self, registry_path):
        self.registry_path = registry_path
        self.models = {}
        self._load_registry()
    
    def _load_registry(self):
        """Carrega registro de modelos externos."""
        if os.path.exists(f"{self.registry_path}/registry.json"):
            with open(f"{self.registry_path}/registry.json") as f:
                self.models = json.load(f)
    
    def _save_registry(self):
        """Salva registro de modelos externos."""
        os.makedirs(self.registry_path, exist_ok=True)
        with open(f"{self.registry_path}/registry.json", "w") as f:
            json.dump(self.models, f, indent=2)
    
    def register_model(self, name, version, model_type, path, metadata=None):
        """Registra modelo externo."""
        if name not in self.models:
            self.models[name] = {}
        
        self.models[name][version] = {
            "type": model_type,
            "path": path,
            "registration_date": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self._save_registry()
        return {"name": name, "version": version}
    
    def get_model_info(self, name, version=None):
        """Obtém informações sobre modelo externo."""
        if name not in self.models:
            raise ValueError(f"Modelo {name} não encontrado no registro")
        
        if version is None:
            # Retornar versão mais recente
            versions = list(self.models[name].keys())
            version = max(versions, key=lambda v: self.models[name][v]["registration_date"])
        
        if version not in self.models[name]:
            raise ValueError(f"Versão {version} do modelo {name} não encontrada")
        
        return {
            "name": name,
            "version": version,
            **self.models[name][version]
        }
```

## Monitoramento de Modelos em Produção

O GEIH implementa monitoramento de modelos em produção para garantir qualidade e desempenho contínuos:

### Métricas de Monitoramento

- **Desempenho do Modelo**: Precisão, recall, F1-score em dados de produção
- **Drift de Dados**: Detecção de mudanças na distribuição de dados de entrada
- **Latência de Predição**: Tempo de resposta para predições
- **Utilização de Recursos**: CPU, memória, armazenamento
- **Logs de Predição**: Registro de predições para auditoria e análise

### Exemplo de Monitoramento

```python
# Exemplo conceitual de monitoramento de modelos
class ModelMonitor:
    """Monitor para modelos em produção."""
    
    def __init__(self, model_name, model_version, metrics_db_path):
        self.model_name = model_name
        self.model_version = model_version
        self.metrics_db_path = metrics_db_path
        self.conn = sqlite3.connect(metrics_db_path)
        self._init_db()
    
    def _init_db(self):
        """Inicializa banco de dados de métricas."""
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT,
            model_version TEXT,
            timestamp TEXT,
            metric_name TEXT,
            metric_value REAL
        )
        ''')
        self.conn.commit()
    
    def log_metric(self, metric_name, metric_value):
        """Registra métrica de modelo."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO model_metrics (model_name, model_version, timestamp, metric_name, metric_value) VALUES (?, ?, ?, ?, ?)",
            (self.model_name, self.model_version, datetime.now().isoformat(), metric_name, metric_value)
        )
        self.conn.commit()
    
    def log_prediction(self, input_data, prediction, ground_truth=None):
        """Registra predição para monitoramento."""
        # Calcular latência
        start_time = time.time()
        # Simulação de predição
        time.sleep(0.01)
        latency = time.time() - start_time
        
        # Registrar métricas
        self.log_metric("prediction_count", 1)
        self.log_metric("prediction_latency", latency)
        
        # Se ground truth estiver disponível, calcular métricas de desempenho
        if ground_truth is not None:
            accuracy = 1 if prediction == ground_truth else 0
            self.log_metric("prediction_accuracy", accuracy)
    
    def check_data_drift(self, reference_data, current_data, feature_names):
        """Verifica drift nos dados de entrada."""
        from scipy.stats import ks_2samp
        
        drift_detected = False
        drift_features = []
        
        for feature in feature_names:
            # Teste Kolmogorov-Smirnov para detectar mudanças na distribuição
            ks_statistic, p_value = ks_2samp(
                reference_data[feature],
                current_data[feature]
            )
            
            # Registrar estatística KS
            self.log_metric(f"drift_{feature}_ks", ks_statistic)
            self.log_metric(f"drift_{feature}_p", p_value)
            
            # Detectar drift significativo (p < 0.05)
            if p_value < 0.05:
                drift_detected = True
                drift_features.append(feature)
        
        # Registrar resultado geral
        self.log_metric("drift_detected", 1 if drift_detected else 0)
        
        return {
            "drift_detected": drift_detected,
            "drift_features": drift_features
        }
    
    def generate_report(self, start_date=None, end_date=None):
        """Gera relatório de monitoramento."""
        # Implementação de relatório de monitoramento
        pass
```

## Diagrama de Fluxo de MLOps

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Desenvolvimento de Modelos                        │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │Preparação│   │Engenharia│   │Seleção de│   │Treinamento│  │Avaliação ││
│  │ de Dados │-->│de Features│-->│ Modelos  │-->│de Modelos │-->│de Modelos││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘│
└───────────────────────────────────────┬─────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Experimentação e Rastreamento                     │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │Versionam.│   │Rastreamen.│   │Registro de│  │Comparação│   │Seleção do││
│  │ de Dados │<->│Experimentos│<->│ Métricas │<->│de Modelos│<->│Melhor Mod││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘│
└───────────────────────────────────────┬─────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Implantação e Monitoramento                       │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │Empacotam.│   │Implantação│   │Serviço de│   │Monitoram.│   │Feedback e││
│  │de Modelos│-->│de Modelos │-->│ Predição │-->│de Modelos│-->│Retraining││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

## Integração com o Restante do Sistema

O fluxo de MLOps do GEIH se integra com outros componentes do sistema:

1. **Pipeline de Dados**: Fornece dados processados para treinamento e avaliação de modelos
2. **API de Serviços**: Consome modelos implantados para fornecer predições via API
3. **Visualização**: Utiliza resultados de modelos para visualizações em dashboards
4. **Alertas**: Utiliza predições para geração de alertas ambientais

## Considerações de Escalabilidade

O fluxo de MLOps do GEIH é projetado para escalar em várias dimensões:

1. **Escala de Modelos**: Suporte a múltiplos tipos de modelos e casos de uso
2. **Escala de Dados**: Capacidade de lidar com volumes crescentes de dados
3. **Escala de Experimentos**: Suporte a experimentação paralela e distribuída
4. **Escala de Implantação**: Capacidade de servir múltiplos modelos em produção

## Próximos Passos

1. **Implementação da Infraestrutura Base**: Setup de MLflow, DVC e estrutura de diretórios
2. **Desenvolvimento de Modelos Iniciais**: Implementação de modelos de risco de incêndio
3. **Integração com Pipeline de Dados**: Conexão com fontes de dados processados
4. **Implementação de Monitoramento**: Setup de monitoramento de modelos em produção
5. **Preparação para Modelos Avançados**: Desenvolvimento de adaptadores para FourCastNet e NVIDIA Modulus

Este fluxo de MLOps foi projetado para atender aos requisitos de análise preditiva do GEIH, com foco inicial em modelos mais simples e interpretáveis, mas com estrutura preparada para integração futura de modelos avançados como FourCastNet e NVIDIA Modulus.
