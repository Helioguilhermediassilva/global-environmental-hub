#!/bin/bash
# Script para inicialização rápida do ambiente de desenvolvimento

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Inicializando ambiente de desenvolvimento do GEIH...${NC}"

# Verificar se está no diretório raiz do projeto
if [ ! -f "README.md" ] || [ ! -d "api" ]; then
    echo -e "${RED}Este script deve ser executado no diretório raiz do projeto.${NC}"
    exit 1
fi

# Configurar ambiente virtual Python
echo -e "${YELLOW}Configurando ambiente virtual Python...${NC}"
bash scripts/setup_venv.sh
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao configurar ambiente virtual Python.${NC}"
    exit 1
fi

# Iniciar serviços Docker
echo -e "${YELLOW}Iniciando serviços Docker...${NC}"
bash scripts/start_docker.sh
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao iniciar serviços Docker.${NC}"
    exit 1
fi

# Verificar status dos serviços
echo -e "${YELLOW}Verificando status dos serviços...${NC}"
sleep 5
curl -s http://localhost:8000/health > /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}API ainda não está disponível. Aguarde alguns instantes e tente acessar http://localhost:8000/health manualmente.${NC}"
else
    echo -e "${GREEN}API está disponível em http://localhost:8000${NC}"
fi

echo -e "${GREEN}Ambiente de desenvolvimento inicializado!${NC}"
echo -e "${YELLOW}Para acessar o dashboard, abra http://localhost:3000 no navegador.${NC}"
echo -e "${YELLOW}Para executar testes e verificações de código, use:${NC}"
echo -e "    bash scripts/run_tests.sh"
