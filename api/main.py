"""Main module for the GEIH API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.presentation.controllers.hotspot_controller import router as hotspot_router

app = FastAPI(
    title="Global Environmental Intelligence Hub API",
    description="API para monitoramento ambiental e análise preditiva",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substitua por origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(hotspot_router)


@app.get("/")
async def root():
    """Endpoint raiz."""
    return {"message": "Bem-vindo à API do Global Environmental Intelligence Hub"}


@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde."""
    return {"status": "healthy", "version": "0.1.0"}
