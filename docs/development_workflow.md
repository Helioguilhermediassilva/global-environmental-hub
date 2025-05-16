# Fluxo de Desenvolvimento e Estrutura de Commits

Este documento descreve o fluxo de desenvolvimento, padrões de código e estrutura de commits para o projeto Global Environmental Intelligence Hub (GEIH).

## Fluxo de Desenvolvimento

O GEIH segue um fluxo de desenvolvimento baseado no GitFlow, adaptado para as necessidades específicas do projeto:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Feature   │────▶│   Develop   │────▶│   Release   │────▶│    Main     │
│  Branches   │     │   Branch    │     │  Branches   │     │   Branch    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                          ▲                                        │
                          │                                        │
                          └────────────────────────────────────────┘
                                       Hotfix Branches
```

### Branches Principais

- **main**: Código em produção, sempre estável
- **develop**: Branch de desenvolvimento, integração de features

### Branches de Suporte

- **feature/\***: Desenvolvimento de novas funcionalidades
- **bugfix/\***: Correção de bugs em desenvolvimento
- **hotfix/\***: Correção de bugs críticos em produção
- **release/\***: Preparação para nova versão

### Ciclo de Vida de uma Feature

1. **Criação da Branch**:
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/nome-da-feature
   ```

2. **Desenvolvimento**:
   - Implementar a funcionalidade
   - Escrever testes
   - Seguir padrões de código
   - Fazer commits frequentes

3. **Testes Locais**:
   ```bash
   # Executar testes unitários
   ./scripts/run_tests.sh
   
   # Iniciar ambiente de desenvolvimento
   ./scripts/dev_init.sh
   
   # Testar manualmente a funcionalidade
   ```

4. **Integração**:
   ```bash
   # Atualizar branch develop
   git checkout develop
   git pull
   
   # Rebase da feature
   git checkout feature/nome-da-feature
   git rebase develop
   
   # Resolver conflitos, se houver
   ```

5. **Pull Request**:
   - Criar PR no GitHub
   - Descrever a funcionalidade
   - Solicitar revisão
   - Aguardar CI/CD

6. **Merge**:
   - Após aprovação, merge na develop
   - Deletar branch de feature

## Estrutura de Commits

O GEIH adota o padrão [Conventional Commits](https://www.conventionalcommits.org/) para mensagens de commit:

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé(s) opcional(is)]
```

### Tipos de Commit

- **feat**: Nova funcionalidade
- **fix**: Correção de bug
- **docs**: Alterações na documentação
- **style**: Alterações que não afetam o código (formatação, etc.)
- **refactor**: Refatoração de código
- **perf**: Melhorias de desempenho
- **test**: Adição ou correção de testes
- **build**: Alterações no sistema de build ou dependências
- **ci**: Alterações nos arquivos de CI
- **chore**: Outras alterações que não modificam código ou testes

### Exemplos

```
feat(api): adiciona endpoint para busca de hotspots por bioma

Implementa novo endpoint que permite filtrar hotspots por bioma,
facilitando a análise de dados específicos por região.

Closes #123
```

```
fix(connector): corrige tratamento de erros no conector NASA FIRMS

O conector não estava tratando corretamente respostas de erro da API,
causando falhas silenciosas durante a ingestão de dados.
```

```
docs(readme): atualiza instruções de instalação

Adiciona detalhes sobre configuração de variáveis de ambiente
e requisitos de sistema.
```

## Padrões de Código

### Python

- **Formatação**: [Black](https://black.readthedocs.io/) com linha máxima de 100 caracteres
- **Imports**: Ordenados com [isort](https://pycqa.github.io/isort/)
- **Linting**: [Flake8](https://flake8.pycqa.org/)
- **Tipagem**: Usar type hints conforme [PEP 484](https://www.python.org/dev/peps/pep-0484/)
- **Docstrings**: Estilo Google

Exemplo:

```python
def calculate_risk_score(
    hotspot: Hotspot, 
    land_use_data: Dict[str, Any], 
    weather_data: Optional[Dict[str, Any]] = None
) -> float:
    """Calcula o score de risco para um hotspot.
    
    Args:
        hotspot: Entidade de hotspot com dados do foco de calor
        land_use_data: Dados de uso do solo para a região do hotspot
        weather_data: Dados meteorológicos opcionais
        
    Returns:
        Score de risco entre 0 e 100
        
    Raises:
        ValueError: Se os dados de uso do solo forem inválidos
    """
    # Implementação
```

### TypeScript/JavaScript

- **Formatação**: [Prettier](https://prettier.io/)
- **Linting**: [ESLint](https://eslint.org/) com configuração para React
- **Tipagem**: TypeScript com tipos explícitos
- **Componentes**: Componentes funcionais com hooks

Exemplo:

```typescript
interface HotspotFilterProps {
  onFilterChange: (filters: FilterCriteria) => void;
  initialFilters?: FilterCriteria;
  isLoading?: boolean;
}

const HotspotFilter: React.FC<HotspotFilterProps> = ({
  onFilterChange,
  initialFilters = { dateRange: '7', source: 'all' },
  isLoading = false,
}) => {
  // Implementação
};
```

## Fluxo de Revisão de Código

1. **Autor**:
   - Implementa a funcionalidade
   - Escreve testes
   - Verifica qualidade do código
   - Cria PR

2. **Revisor**:
   - Verifica se o código segue os padrões
   - Verifica se os testes cobrem a funcionalidade
   - Verifica se a documentação está atualizada
   - Sugere melhorias

3. **Autor**:
   - Implementa as sugestões
   - Responde aos comentários
   - Atualiza o PR

4. **Revisor**:
   - Aprova o PR ou solicita mais alterações

5. **Mantenedor**:
   - Realiza o merge após aprovação

## Fluxo de Testes

### Testes Unitários

- Testar componentes isoladamente
- Usar mocks para dependências externas
- Focar em comportamento, não implementação

### Testes de Integração

- Testar interação entre componentes
- Verificar fluxo de dados
- Usar banco de dados de teste

### Testes End-to-End

- Testar fluxo completo
- Simular interação do usuário
- Verificar comportamento do sistema como um todo

## Exemplos de Uso

### Desenvolvimento de Nova Funcionalidade

```bash
# 1. Criar branch de feature
git checkout develop
git pull
git checkout -b feature/filtro-por-bioma

# 2. Implementar funcionalidade
# Editar arquivos...

# 3. Executar testes
./scripts/run_tests.sh

# 4. Fazer commit
git add .
git commit -m "feat(api): adiciona filtro por bioma no endpoint de hotspots"

# 5. Integrar com develop
git checkout develop
git pull
git checkout feature/filtro-por-bioma
git rebase develop

# 6. Resolver conflitos (se houver)
# Editar arquivos...
git add .
git rebase --continue

# 7. Push para o repositório remoto
git push -u origin feature/filtro-por-bioma

# 8. Criar Pull Request no GitHub
# Usar interface web do GitHub
```

### Correção de Bug

```bash
# 1. Criar branch de bugfix
git checkout develop
git pull
git checkout -b bugfix/correcao-parser-csv

# 2. Implementar correção
# Editar arquivos...

# 3. Executar testes
./scripts/run_tests.sh

# 4. Fazer commit
git add .
git commit -m "fix(ingestao): corrige parser de CSV para lidar com valores vazios"

# 5. Push para o repositório remoto
git push -u origin bugfix/correcao-parser-csv

# 6. Criar Pull Request no GitHub
# Usar interface web do GitHub
```

## Integração Contínua

O GEIH utiliza GitHub Actions para CI/CD:

1. **Lint e Formatação**: Verificação automática de estilo de código
2. **Testes**: Execução de testes unitários e de integração
3. **Build**: Construção de artefatos
4. **Deploy**: Implantação em ambiente de preview (para PRs)

Cada PR deve passar por todas as verificações antes de ser aprovado.

## Versionamento

O GEIH segue o [Semantic Versioning](https://semver.org/):

- **MAJOR**: Mudanças incompatíveis com versões anteriores
- **MINOR**: Adições de funcionalidades compatíveis
- **PATCH**: Correções de bugs compatíveis

Exemplo: 1.2.3

## Documentação

- **Código**: Docstrings e comentários
- **API**: Documentação automática com Swagger/OpenAPI
- **Arquitetura**: Documentação em Markdown
- **Usuário**: Guias e tutoriais

## Conclusão

Seguir este fluxo de desenvolvimento e estrutura de commits garante:

- Código de alta qualidade
- Rastreabilidade de mudanças
- Facilidade de colaboração
- Processo de revisão eficiente
- Integração contínua
- Entrega contínua

Para dúvidas ou sugestões, abra uma issue no repositório.
