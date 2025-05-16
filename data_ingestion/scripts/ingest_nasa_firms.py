"""Script para ingestão de dados do NASA FIRMS."""
import asyncio
import csv
import json
import os
import uuid
from datetime import datetime

import aiohttp
from dotenv import load_dotenv

from data_ingestion.connectors.nasa_firms_connector import NASAFirmsConnector

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
API_KEY = os.getenv("NASA_FIRMS_API_KEY", "sua_chave_api_aqui")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
AMAZON_BBOX = (-73.9904, -18.0414, -44.0005, 5.2672)  # Bounding box aproximado da Amazônia Legal


async def ingest_nasa_firms_data():
    """Ingerir dados do NASA FIRMS para a Amazônia Legal."""
    # Garantir que o diretório de saída exista
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Criar conector
    connector = NASAFirmsConnector(api_key=API_KEY)
    
    try:
        # Conectar à API
        connected = await connector.connect()
        if not connected:
            print("Falha ao conectar à API NASA FIRMS. Verifique sua chave API.")
            return
        
        print("Conectado à API NASA FIRMS com sucesso.")
        
        # Definir parâmetros para a consulta
        # Formato: YYYY-MM-DD
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        
        parameters = {
            "area": f"{AMAZON_BBOX[1]},{AMAZON_BBOX[0]},{AMAZON_BBOX[3]},{AMAZON_BBOX[2]}",
            "date_range": f"{week_ago}/{today}",
            "satellite": "VIIRS",
            "format": "csv"
        }
        
        print(f"Buscando dados para o período: {week_ago} a {today}")
        
        # Buscar dados
        result = await connector.fetch_data(parameters)
        
        # Validar dados
        if not await connector.validate_data(result):
            print("Dados inválidos ou vazios recebidos da API.")
            return
        
        # Processar dados
        if result.get("format") == "csv":
            # Salvar CSV bruto
            csv_path = os.path.join(OUTPUT_DIR, f"nasa_firms_{week_ago}_to_{today}.csv")
            with open(csv_path, "w", newline="") as f:
                f.write(result["data"])
            
            print(f"Dados brutos salvos em: {csv_path}")
            
            # Processar CSV para formato JSON compatível com a API
            json_path = os.path.join(OUTPUT_DIR, f"nasa_firms_{week_ago}_to_{today}.json")
            hotspots = []
            
            # Ler CSV e converter para formato de hotspot
            csv_data = result["data"].strip().split("\n")
            reader = csv.DictReader(csv_data)
            
            for row in reader:
                try:
                    hotspot = {
                        "id": f"FIRMS_{uuid.uuid4().hex[:8]}",
                        "latitude": float(row.get("latitude")),
                        "longitude": float(row.get("longitude")),
                        "acquisition_date": datetime.strptime(
                            f"{row.get('acq_date')} {row.get('acq_time')}", 
                            "%Y-%m-%d %H%M"
                        ).isoformat(),
                        "confidence": int(float(row.get("confidence", 0))),
                        "source": "VIIRS",
                        "brightness": float(row.get("bright_ti4", 0)),
                        "frp": float(row.get("frp", 0)),
                        "biome": "Amazon Rainforest",  # Simplificação - em produção, usar dados geoespaciais
                        "land_use": None  # Seria preenchido com dados de uso do solo
                    }
                    hotspots.append(hotspot)
                except (ValueError, KeyError) as e:
                    print(f"Erro ao processar linha: {e}")
                    continue
            
            # Salvar JSON processado
            with open(json_path, "w") as f:
                json.dump(hotspots, f, indent=2)
            
            print(f"Dados processados salvos em: {json_path}")
            print(f"Total de hotspots processados: {len(hotspots)}")
            
            return hotspots
        else:
            print(f"Formato não suportado: {result.get('format')}")
            return None
    
    except Exception as e:
        print(f"Erro durante a ingestão de dados: {e}")
        return None
    
    finally:
        # Fechar conexão
        await connector.close()
        print("Conexão fechada.")


async def upload_hotspots_to_api(hotspots, api_url="http://localhost:8000/api/hotspots/batch"):
    """Fazer upload dos hotspots para a API."""
    if not hotspots:
        print("Nenhum hotspot para enviar.")
        return
    
    print(f"Enviando {len(hotspots)} hotspots para a API...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api_url, json=hotspots) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"Upload concluído com sucesso. {result.get('processed', 0)} hotspots processados.")
                else:
                    print(f"Falha no upload. Status: {response.status}")
                    print(await response.text())
        except Exception as e:
            print(f"Erro durante o upload: {e}")


if __name__ == "__main__":
    # Executar ingestão
    hotspots = asyncio.run(ingest_nasa_firms_data())
    
    # Fazer upload para API (comentado até a API estar pronta)
    # if hotspots:
    #     asyncio.run(upload_hotspots_to_api(hotspots))
