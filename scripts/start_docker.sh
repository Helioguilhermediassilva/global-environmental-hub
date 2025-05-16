#!/bin/bash
# Script para iniciar os serviços Docker do GEIH

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Iniciando serviços Docker para o GEIH...${NC}"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker não encontrado. Por favor, instale o Docker.${NC}"
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose não encontrado. Por favor, instale o Docker Compose.${NC}"
    exit 1
fi

# Construir e iniciar os containers
echo -e "${YELLOW}Construindo e iniciando containers...${NC}"
docker-compose up -d --build

if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao iniciar os serviços Docker.${NC}"
    exit 1
fi

echo -e "${GREEN}Serviços Docker iniciados com sucesso!${NC}"
echo -e "${YELLOW}Para verificar os logs, execute:${NC}"
echo -e "    docker-compose logs -f"
echo -e "${YELLOW}Para parar os serviços, execute:${NC}"
echo -e "    docker-compose down"

# Mostrar status dos serviços
echo -e "${YELLOW}Status dos serviços:${NC}"
docker-compose ps
