#!/bin/bash
# Script para configurar ambiente virtual Python para o GEIH

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Iniciando configuração do ambiente virtual Python para o GEIH...${NC}"

# Verificar se Python 3.11 está instalado
if ! command -v python3.11 &> /dev/null; then
    echo -e "${RED}Python 3.11 não encontrado. Por favor, instale o Python 3.11.${NC}"
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Criando ambiente virtual...${NC}"
    python3.11 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Falha ao criar ambiente virtual.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Ambiente virtual criado com sucesso.${NC}"
else
    echo -e "${YELLOW}Ambiente virtual já existe.${NC}"
fi

# Ativar ambiente virtual
echo -e "${YELLOW}Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Atualizar pip
echo -e "${YELLOW}Atualizando pip...${NC}"
pip install --upgrade pip

# Instalar dependências
echo -e "${YELLOW}Instalando dependências...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao instalar dependências.${NC}"
    exit 1
fi

# Instalar dependências de desenvolvimento
echo -e "${YELLOW}Instalando dependências de desenvolvimento...${NC}"
pip install -r requirements-dev.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao instalar dependências de desenvolvimento.${NC}"
    exit 1
fi

echo -e "${GREEN}Ambiente virtual configurado com sucesso!${NC}"
echo -e "${YELLOW}Para ativar o ambiente virtual, execute:${NC}"
echo -e "    source venv/bin/activate"

# Manter ambiente ativado
echo -e "${YELLOW}Ambiente virtual está ativado.${NC}"
