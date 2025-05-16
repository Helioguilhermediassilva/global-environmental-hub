"""DAG para ingestão de dados do NASA FIRMS."""
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
    """Ingerir dados do NASA FIRMS API."""
    import asyncio
    import sys
    import os
    
    # Adicionar diretório raiz ao path para importar módulos do projeto
    sys.path.append('/opt/airflow/dags/repo')
    
    from data_ingestion.scripts.ingest_nasa_firms import ingest_nasa_firms_data as ingest_func
    
    # Executar função de ingestão
    hotspots = asyncio.run(ingest_func())
    
    # Retornar estatísticas para o Airflow
    return {
        "status": "success" if hotspots else "error",
        "records": len(hotspots) if hotspots else 0,
        "timestamp": datetime.now().isoformat()
    }


def validate_nasa_firms_data(**kwargs):
    """Validar dados do NASA FIRMS."""
    ti = kwargs['ti']
    ingest_result = ti.xcom_pull(task_ids='ingest_nasa_firms_data')
    
    if not ingest_result or ingest_result.get('status') != 'success':
        raise ValueError("Falha na ingestão de dados. Validação cancelada.")
    
    records = ingest_result.get('records', 0)
    
    # Validação simples baseada no número de registros
    if records == 0:
        raise ValueError("Nenhum registro encontrado para validação.")
    
    # Em um cenário real, faríamos validações mais complexas aqui
    valid_records = records
    invalid_records = 0
    
    return {
        "status": "success",
        "total_records": records,
        "valid_records": valid_records,
        "invalid_records": invalid_records
    }


def transform_nasa_firms_data(**kwargs):
    """Transformar dados do NASA FIRMS para formato padrão."""
    ti = kwargs['ti']
    validate_result = ti.xcom_pull(task_ids='validate_nasa_firms_data')
    
    if not validate_result or validate_result.get('status') != 'success':
        raise ValueError("Falha na validação de dados. Transformação cancelada.")
    
    # Em um cenário real, faríamos transformações mais complexas aqui
    # Por exemplo, enriquecimento com dados de biomas, uso do solo, etc.
    
    return {
        "status": "success",
        "transformed_records": validate_result.get('valid_records', 0),
        "timestamp": datetime.now().isoformat()
    }


def load_nasa_firms_data(**kwargs):
    """Carregar dados do NASA FIRMS na base de dados."""
    ti = kwargs['ti']
    transform_result = ti.xcom_pull(task_ids='transform_nasa_firms_data')
    
    if not transform_result or transform_result.get('status') != 'success':
        raise ValueError("Falha na transformação de dados. Carregamento cancelado.")
    
    # Em um cenário real, carregaríamos os dados no banco de dados aqui
    # Por exemplo, usando SQLAlchemy para inserir no PostgreSQL
    
    return {
        "status": "success",
        "loaded_records": transform_result.get('transformed_records', 0),
        "timestamp": datetime.now().isoformat()
    }


with DAG(
    "nasa_firms_ingestion",
    default_args=default_args,
    description="Ingestão de dados do NASA FIRMS API",
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
    
    load_task = PythonOperator(
        task_id="load_nasa_firms_data",
        python_callable=load_nasa_firms_data,
    )

    # Definir dependências entre tarefas
    ingest_task >> validate_task >> transform_task >> load_task
