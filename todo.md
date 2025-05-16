# Global Environmental Intelligence Hub (GEIH) - Lista de Tarefas

## Ciclo 1: Estruturação e Documentação (Concluído)
- [x] Analisar requisitos do projeto
- [x] Elaborar perguntas de clarificação para o usuário
- [x] Aguardar confirmação do usuário
- [x] Definir escopo inicial e prioridades
- [x] Estruturar árvore de diretórios e arquivos base
- [x] Planejar arquitetura limpa e hexagonal
- [x] Selecionar stack tecnológica e ferramentas
- [x] Propor fluxo de dados e pipeline de ingestão
- [x] Desenhar fluxo de MLOps e experimentos
- [x] Definir políticas de observabilidade e segurança
- [x] Planejar estrutura de CI/CD e DevOps
- [x] Criar documentação inicial no README
- [x] Validar estrutura com usuário
- [x] Ajustar escopo e diretórios se necessário
- [x] Reportar e enviar estrutura ao usuário

## Ciclo 2: Desenvolvimento Incremental (Em Andamento)
- [x] Preparar ambiente para desenvolvimento contínuo
  - [x] Configurar ambiente virtual Python
  - [x] Instalar dependências básicas
  - [x] Configurar Docker e Docker Compose
  - [x] Preparar scripts de inicialização
  - [x] Configurar ambiente de desenvolvimento local
- [x] Implementar módulos iniciais de API e conectores
  - [x] Desenvolver estrutura base da API FastAPI
  - [x] Implementar conector para NASA FIRMS
  - [x] Criar modelos de domínio para hotspots
  - [x] Desenvolver repositórios e casos de uso
- [x] Criar exemplo funcional de ingestão e visualização
  - [x] Implementar script de ingestão de dados FIRMS
  - [x] Desenvolver endpoint para consulta de hotspots
  - [x] Criar visualização básica de mapa com dados
- [x] Desenvolver fluxo mínimo de pipeline no Airflow
  - [x] Configurar DAG para ingestão periódica
  - [x] Implementar operadores para processamento
  - [x] Criar tarefas de validação e transformação
- [x] Implementar testes unitários e integração
  - [x] Desenvolver testes para conectores
  - [x] Criar testes para API e endpoints
  - [x] Implementar testes para pipeline de dados
- [x] Configurar MVP do dashboard com visualização básica
  - [x] Desenvolver componentes React para mapa
  - [x] Implementar filtros básicos
  - [x] Criar visualização de estatísticas
- [x] Documentar fluxo de desenvolvimento e estrutura de commits
- [x] Validar funcionalidade mínima localmente
- [x] Revisar e ajustar código conforme feedback
- [x] Preparar arquivos para commit inicial no GitHub
- [x] Criar guia de publicação e fluxo Git
- [ ] Gerar pacote completo para upload no GitHub
- [ ] Reportar ao usuário com arquivos e guia
- [ ] Aguardar feedback para ajustes finais
- [ ] Finalizar e documentar entrega

## Escopo Inicial e Prioridades
- Foco geográfico: Amazônia Legal
- Prioridades funcionais:
  1. Monitoramento contínuo de dados ambientais via satélite, com visualização geoespacial
  2. Estrutura modular para futura integração de análise preditiva avançada
- Fontes de dados iniciais:
  - NASA FIRMS (MODIS/VIIRS)
  - BDQueimadas (INPE)
- Usuários-alvo:
  - Pesquisadores e cientistas ambientais
  - Agências públicas (IBAMA, ICMBio, Defesa Civil)
  - ONGs e instituições internacionais
