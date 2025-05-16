#!/bin/bash
# Script para executar testes e verificações de qualidade de código

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Executando testes e verificações de qualidade de código...${NC}"

# Verificar se o ambiente virtual está ativado
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}Ambiente virtual não ativado. Ativando...${NC}"
    source venv/bin/activate
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo -e "${RED}Falha ao ativar ambiente virtual. Execute 'source venv/bin/activate' manualmente.${NC}"
        exit 1
    fi
fi

# Executar verificação de formatação com Black
echo -e "${YELLOW}Verificando formatação com Black...${NC}"
black --check .
if [ $? -ne 0 ]; then
    echo -e "${RED}Problemas de formatação encontrados. Execute 'black .' para corrigir.${NC}"
    exit 1
fi
echo -e "${GREEN}Formatação verificada com sucesso!${NC}"

# Executar verificação de imports com isort
echo -e "${YELLOW}Verificando imports com isort...${NC}"
isort --check .
if [ $? -ne 0 ]; then
    echo -e "${RED}Problemas de ordenação de imports encontrados. Execute 'isort .' para corrigir.${NC}"
    exit 1
fi
echo -e "${GREEN}Imports verificados com sucesso!${NC}"

# Executar verificação de linting com flake8
echo -e "${YELLOW}Verificando linting com flake8...${NC}"
flake8 .
if [ $? -ne 0 ]; then
    echo -e "${RED}Problemas de linting encontrados. Corrija os problemas indicados acima.${NC}"
    exit 1
fi
echo -e "${GREEN}Linting verificado com sucesso!${NC}"

# Executar testes com pytest
echo -e "${YELLOW}Executando testes com pytest...${NC}"
pytest
if [ $? -ne 0 ]; then
    echo -e "${RED}Alguns testes falharam. Corrija os problemas indicados acima.${NC}"
    exit 1
fi
echo -e "${GREEN}Todos os testes passaram com sucesso!${NC}"

echo -e "${GREEN}Todas as verificações de qualidade de código passaram!${NC}"
