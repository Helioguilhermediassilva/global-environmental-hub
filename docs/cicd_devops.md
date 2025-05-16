# CI/CD e DevOps do Global Environmental Intelligence Hub (GEIH)

Este documento detalha a estrutura de CI/CD (Integração Contínua e Entrega Contínua) e práticas DevOps do Global Environmental Intelligence Hub (GEIH), descrevendo os pipelines de automação, ferramentas, configurações e melhores práticas para garantir qualidade, confiabilidade e agilidade no desenvolvimento.

## Visão Geral da Estratégia de CI/CD

O GEIH adota uma abordagem moderna de CI/CD baseada em GitHub Actions, com foco em automação, testes contínuos e feedback rápido:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Commit   │ -> │  Lint e     │ -> │   Testes    │ -> │   Build     │ -> │   Deploy    │
│             │    │  Formatação │    │             │    │             │    │  Simulado   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Estrutura de Diretórios para CI/CD

```
.github/
├── workflows/
│   ├── ci.yml                  # Pipeline principal de CI
│   ├── python-lint.yml         # Lint e formatação para Python
│   ├── js-lint.yml             # Lint e formatação para JavaScript/TypeScript
│   ├── python-tests.yml        # Testes para componentes Python
│   ├── js-tests.yml            # Testes para componentes JavaScript/TypeScript
│   ├── build.yml               # Build de artefatos
│   ├── deploy-preview.yml      # Deploy para ambiente de preview
│   └── security-scan.yml       # Análise de segurança
│
├── actions/                    # Ações personalizadas
│   ├── setup-environment/      # Ação para configurar ambiente
│   └── data-validation/        # Ação para validação de dados
│
└── CODEOWNERS                  # Definição de proprietários de código
```

## Workflows de GitHub Actions

### CI Principal

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Lint with flake8
        run: flake8 .
      - name: Check formatting with black
        run: black --check .
      - name: Check imports with isort
        run: isort --check .
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install JS dependencies
        run: |
          cd dashboards
          npm ci
      - name: Lint with ESLint
        run: |
          cd dashboards
          npm run lint
      - name: Check formatting with Prettier
        run: |
          cd dashboards
          npm run format:check

  test:
    name: Test
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:14-3.3
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_USER: postgres
          POSTGRES_DB: test_geih
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:6.2-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      minio:
        image: minio/minio
        env:
          MINIO_ROOT_USER: minioadmin
          MINIO_ROOT_PASSWORD: minioadmin
        ports:
          - 9000:9000
        options: >-
          --health-cmd "curl -f http://localhost:9000/minio/health/live"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        volumes:
          - /tmp/minio-data:/data
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Run Python tests
        run: pytest --cov=. --cov-report=xml
        env:
          POSTGRES_HOST: localhost
          POSTGRES_PORT: 5432
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_geih
          REDIS_HOST: localhost
          REDIS_PORT: 6379
          MINIO_HOST: localhost
          MINIO_PORT: 9000
          MINIO_ACCESS_KEY: minioadmin
          MINIO_SECRET_KEY: minioadmin
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install JS dependencies
        run: |
          cd dashboards
          npm ci
      - name: Run JS tests
        run: |
          cd dashboards
          npm test -- --coverage
      - name: Upload JS coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./dashboards/coverage/coverage-final.json
          fail_ci_if_error: true

  build:
    name: Build
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install build wheel
      - name: Build Python packages
        run: |
          python -m build
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install JS dependencies
        run: |
          cd dashboards
          npm ci
      - name: Build frontend
        run: |
          cd dashboards
          npm run build
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-artifacts
          path: |
            dist/
            dashboards/build/

  deploy-preview:
    name: Deploy Preview
    if: github.event_name == 'pull_request'
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-artifacts
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - name: Build and push Docker images
        uses: docker/build-push-action@v4
        with:
          context: .
          push: false
          tags: geih-preview:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - name: Deploy to preview environment
        run: |
          echo "Deploying to preview environment..."
          # Simulação de deploy para ambiente de preview
          echo "Preview URL: https://preview-${{ github.sha }}.geih.org"
          echo "Preview URL: https://preview-${{ github.sha }}.geih.org" >> $GITHUB_STEP_SUMMARY
```

### Workflow de Testes Python

```yaml
# .github/workflows/python-tests.yml
name: Python Tests

on:
  push:
    branches: [ main, develop ]
    paths:
      - '**.py'
      - 'requirements*.txt'
      - '.github/workflows/python-tests.yml'
  pull_request:
    branches: [ main, develop ]
    paths:
      - '**.py'
      - 'requirements*.txt'
      - '.github/workflows/python-tests.yml'

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    services:
      postgres:
        image: postgis/postgis:14-3.3
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_USER: postgres
          POSTGRES_DB: test_geih
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml
        env:
          POSTGRES_HOST: localhost
          POSTGRES_PORT: 5432
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_geih
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

### Workflow de Análise de Segurança

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 0 * * 0'  # Executa semanalmente aos domingos

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install bandit safety
      - name: Run Bandit
        run: bandit -r . -x ./tests,./venv
      - name: Run Safety
        run: safety check
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install JS dependencies
        run: |
          cd dashboards
          npm ci
      - name: Run npm audit
        run: |
          cd dashboards
          npm audit
      - name: Run OWASP Dependency-Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'GEIH'
          path: '.'
          format: 'HTML'
          out: 'reports'
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: dependency-check-report
          path: reports
```

## Configuração de Ambientes

### Ambientes de Desenvolvimento

```yaml
# .github/workflows/setup-dev-environment.yml
name: Setup Development Environment

on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 1 * *'  # Executa mensalmente

jobs:
  setup-dev:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Docker Compose
        run: |
          docker-compose -f docker-compose.dev.yml up -d
      - name: Initialize database
        run: |
          docker-compose -f docker-compose.dev.yml exec -T api python scripts/init_db.py
      - name: Load sample data
        run: |
          docker-compose -f docker-compose.dev.yml exec -T api python scripts/load_sample_data.py
      - name: Run smoke tests
        run: |
          docker-compose -f docker-compose.dev.yml exec -T api pytest tests/smoke
      - name: Generate development documentation
        run: |
          docker-compose -f docker-compose.dev.yml exec -T api sphinx-build -b html docs/source docs/build
      - name: Upload documentation
        uses: actions/upload-artifact@v3
        with:
          name: dev-docs
          path: docs/build
```

### Docker Compose para Desenvolvimento

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=geih_dev
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - MINIO_HOST=minio
      - MINIO_PORT=9000
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
    depends_on:
      - postgres
      - redis
      - minio

  postgres:
    image: postgis/postgis:14-3.3
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_DB=geih_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  dashboard:
    build:
      context: ./dashboards
      dockerfile: Dockerfile.dev
    volumes:
      - ./dashboards:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - NODE_ENV=development
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

## Dockerfiles

### Dockerfile para API

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código-fonte
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile para Dashboard

```dockerfile
# dashboards/Dockerfile
FROM node:20-alpine as build

WORKDIR /app

# Copiar arquivos de configuração e instalar dependências
COPY package*.json ./
RUN npm ci

# Copiar código-fonte e construir aplicação
COPY . .
RUN npm run build

# Estágio de produção
FROM nginx:alpine

# Copiar build da aplicação para o diretório do Nginx
COPY --from=build /app/build /usr/share/nginx/html

# Copiar configuração personalizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## Configuração de Testes

### Pytest

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = --cov=. --cov-report=term --cov-report=xml --cov-report=html
markers =
    unit: marks tests as unit tests
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    slow: marks tests as slow
```

### Jest

```json
// dashboards/jest.config.js
module.exports = {
  collectCoverage: true,
  collectCoverageFrom: [
    "src/**/*.{js,jsx,ts,tsx}",
    "!src/**/*.d.ts",
    "!src/index.tsx",
    "!src/serviceWorker.ts",
    "!src/reportWebVitals.ts"
  ],
  coverageDirectory: "coverage",
  testEnvironment: "jsdom",
  setupFilesAfterEnv: [
    "<rootDir>/src/setupTests.ts"
  ],
  transform: {
    "^.+\\.(js|jsx|ts|tsx)$": "babel-jest"
  },
  moduleNameMapper: {
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
    "\\.(jpg|jpeg|png|gif|webp|svg)$": "<rootDir>/__mocks__/fileMock.js"
  }
};
```

## Ferramentas de Qualidade de Código

### Configuração do Flake8

```ini
# .flake8
[flake8]
max-line-length = 100
exclude = .git,__pycache__,build,dist,venv
ignore = E203, W503
per-file-ignores =
    __init__.py:F401
    tests/*:S101
```

### Configuração do Black

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

### Configuração do isort

```toml
# pyproject.toml
[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["*/migrations/*", "venv/*"]
```

### Configuração do ESLint

```json
// dashboards/.eslintrc.json
{
  "env": {
    "browser": true,
    "es2021": true,
    "jest": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:prettier/recommended"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaFeatures": {
      "jsx": true
    },
    "ecmaVersion": 12,
    "sourceType": "module"
  },
  "plugins": [
    "react",
    "react-hooks",
    "@typescript-eslint"
  ],
  "rules": {
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "react/prop-types": "off",
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off"
  },
  "settings": {
    "react": {
      "version": "detect"
    }
  }
}
```

### Configuração do Prettier

```json
// dashboards/.prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "endOfLine": "lf"
}
```

## Estratégia de Branches e Releases

O GEIH adota o modelo GitFlow para gerenciamento de branches:

### Branches Principais

- **main**: Código em produção, sempre estável
- **develop**: Branch de desenvolvimento, integração de features

### Branches de Suporte

- **feature/\***: Desenvolvimento de novas funcionalidades
- **bugfix/\***: Correção de bugs em desenvolvimento
- **hotfix/\***: Correção de bugs críticos em produção
- **release/\***: Preparação para nova versão

### Fluxo de Trabalho

1. Desenvolvimento de novas funcionalidades em branches `feature/*`
2. Integração de features concluídas em `develop`
3. Criação de branch `release/*` para preparação de versão
4. Testes e correções finais na branch de release
5. Merge da release em `main` e `develop`
6. Criação de tag de versão

### Convenções de Commit

O GEIH adota o padrão Conventional Commits para mensagens de commit:

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé(s) opcional(is)]
```

Tipos principais:
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

## Automação de Releases

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build wheel twine
      - name: Build Python packages
        run: |
          python -m build
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install JS dependencies
        run: |
          cd dashboards
          npm ci
      - name: Build frontend
        run: |
          cd dashboards
          npm run build
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: geih/api,geih/dashboard
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
      - name: Build and push API image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
      - name: Build and push Dashboard image
        uses: docker/build-push-action@v4
        with:
          context: ./dashboards
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
      - name: Create Release
        id: create_release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
      - name: Upload Release Assets
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: ./dist/*.whl
          asset_name: geih-${{ github.ref }}.whl
          asset_content_type: application/octet-stream
```

## Monitoramento de Dependências

```yaml
# .github/workflows/dependency-updates.yml
name: Dependency Updates

on:
  schedule:
    - cron: '0 0 * * 1'  # Executa toda segunda-feira
  workflow_dispatch:

jobs:
  update-dependencies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install pip-tools
        run: |
          python -m pip install --upgrade pip
          pip install pip-tools
      - name: Update Python dependencies
        run: |
          pip-compile --upgrade requirements.in
          pip-compile --upgrade requirements-dev.in
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Update JS dependencies
        run: |
          cd dashboards
          npm update
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: 'chore: update dependencies'
          title: 'chore: update dependencies'
          body: |
            Automated dependency updates.
            
            - Updated Python dependencies
            - Updated JavaScript dependencies
          branch: dependency-updates
          base: develop
```

## Integração com Ferramentas de Qualidade

```yaml
# .github/workflows/code-quality.yml
name: Code Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  sonarcloud:
    name: SonarCloud
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          args: >
            -Dsonar.projectKey=geih
            -Dsonar.organization=geih
            -Dsonar.python.coverage.reportPaths=coverage.xml
            -Dsonar.javascript.lcov.reportPaths=dashboards/coverage/lcov.info
  
  codacy:
    name: Codacy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Codacy Analysis CLI
        uses: codacy/codacy-analysis-cli-action@master
        with:
          project-token: ${{ secrets.CODACY_PROJECT_TOKEN }}
          upload: true
          max-allowed-issues: 10
```

## Documentação Automatizada

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [ main, develop ]
    paths:
      - '**.py'
      - '**.md'
      - 'docs/**'
      - '.github/workflows/docs.yml'

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
          pip install sphinx sphinx-rtd-theme myst-parser
      - name: Build documentation
        run: |
          cd docs
          make html
      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/build/html
```

## Infraestrutura como Código

### Terraform para AWS

```hcl
# infra/terraform/main.tf
provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "geih-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway = true
  single_nat_gateway = true
  
  tags = {
    Environment = var.environment
    Project     = "geih"
  }
}

module "ecs" {
  source = "terraform-aws-modules/ecs/aws"
  
  name = "geih-cluster"
  
  container_insights = true
  
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  
  default_capacity_provider_strategy = [
    {
      capacity_provider = "FARGATE"
      weight            = 1
      base              = 1
    },
    {
      capacity_provider = "FARGATE_SPOT"
      weight            = 4
    }
  ]
  
  tags = {
    Environment = var.environment
    Project     = "geih"
  }
}

module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  
  identifier = "geih-postgres"
  
  engine            = "postgres"
  engine_version    = "14.3"
  instance_class    = "db.t3.medium"
  allocated_storage = 20
  
  db_name  = "geih"
  username = var.db_username
  password = var.db_password
  port     = "5432"
  
  vpc_security_group_ids = [module.security_group.security_group_id]
  subnet_ids             = module.vpc.private_subnets
  
  family = "postgres14"
  
  major_engine_version = "14"
  
  deletion_protection = true
  
  tags = {
    Environment = var.environment
    Project     = "geih"
  }
}

module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"
  
  bucket = "geih-data-lake-${var.environment}"
  acl    = "private"
  
  versioning = {
    enabled = true
  }
  
  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }
  
  tags = {
    Environment = var.environment
    Project     = "geih"
  }
}

module "security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  
  name        = "geih-sg"
  description = "Security group for GEIH"
  vpc_id      = module.vpc.vpc_id
  
  ingress_cidr_blocks = ["0.0.0.0/0"]
  ingress_rules       = ["https-443-tcp", "http-80-tcp"]
  
  egress_rules = ["all-all"]
  
  tags = {
    Environment = var.environment
    Project     = "geih"
  }
}
```

### Docker Compose para Produção

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  traefik:
    image: traefik:v2.6
    command:
      - "--api.insecure=false"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.web.http.redirections.entryPoint.to=websecure"
      - "--entrypoints.web.http.redirections.entryPoint.scheme=https"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=${ACME_EMAIL}"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-data:/letsencrypt
    networks:
      - geih-network
    restart: always

  api:
    image: geih/api:${TAG:-latest}
    environment:
      - ENVIRONMENT=production
      - POSTGRES_HOST=${POSTGRES_HOST}
      - POSTGRES_PORT=${POSTGRES_PORT}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PORT=${REDIS_PORT}
      - MINIO_HOST=${MINIO_HOST}
      - MINIO_PORT=${MINIO_PORT}
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
      - JWT_SECRET=${JWT_SECRET}
    networks:
      - geih-network
    restart: always
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.geih.org`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls.certresolver=myresolver"
      - "traefik.http.services.api.loadbalancer.server.port=8000"

  dashboard:
    image: geih/dashboard:${TAG:-latest}
    networks:
      - geih-network
    restart: always
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard.rule=Host(`geih.org`)"
      - "traefik.http.routers.dashboard.entrypoints=websecure"
      - "traefik.http.routers.dashboard.tls.certresolver=myresolver"
      - "traefik.http.services.dashboard.loadbalancer.server.port=80"

  prometheus:
    image: prom/prometheus:v2.37.0
    volumes:
      - ./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    networks:
      - geih-network
    restart: always
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.prometheus.rule=Host(`prometheus.geih.org`)"
      - "traefik.http.routers.prometheus.entrypoints=websecure"
      - "traefik.http.routers.prometheus.tls.certresolver=myresolver"
      - "traefik.http.services.prometheus.loadbalancer.server.port=9090"
      - "traefik.http.routers.prometheus.middlewares=prometheus-auth"
      - "traefik.http.middlewares.prometheus-auth.basicauth.users=${PROMETHEUS_AUTH}"

  grafana:
    image: grafana/grafana:9.0.0
    volumes:
      - ./infra/grafana/provisioning:/etc/grafana/provisioning
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    networks:
      - geih-network
    restart: always
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.grafana.rule=Host(`grafana.geih.org`)"
      - "traefik.http.routers.grafana.entrypoints=websecure"
      - "traefik.http.routers.grafana.tls.certresolver=myresolver"
      - "traefik.http.services.grafana.loadbalancer.server.port=3000"

networks:
  geih-network:
    driver: bridge

volumes:
  traefik-data:
  prometheus-data:
  grafana-data:
```

## Melhores Práticas de DevOps

### 1. Automação Contínua

- **Princípio**: Automatizar todos os processos repetitivos
- **Implementação**: Uso de GitHub Actions para CI/CD, Terraform para IaC
- **Benefícios**: Redução de erros humanos, maior velocidade, consistência

### 2. Infraestrutura como Código (IaC)

- **Princípio**: Gerenciar infraestrutura através de código versionado
- **Implementação**: Uso de Terraform para AWS, Docker Compose para ambientes locais
- **Benefícios**: Reprodutibilidade, versionamento, documentação implícita

### 3. Monitoramento e Observabilidade

- **Princípio**: Visibilidade completa do sistema em produção
- **Implementação**: Prometheus, Grafana, Loguru, OpenTelemetry
- **Benefícios**: Detecção precoce de problemas, diagnóstico eficiente

### 4. Segurança Integrada (DevSecOps)

- **Princípio**: Segurança como parte integral do ciclo de desenvolvimento
- **Implementação**: Análise de dependências, SAST, DAST, verificação de conformidade
- **Benefícios**: Detecção precoce de vulnerabilidades, redução de riscos

### 5. Cultura de Melhoria Contínua

- **Princípio**: Aprendizado e evolução constantes
- **Implementação**: Retrospectivas, análise de métricas, experimentação
- **Benefícios**: Adaptabilidade, inovação, qualidade crescente

## Diagrama de Fluxo de CI/CD

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Desenvolvimento                                   │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │  Código  │-->│  Commit  │-->│   Push   │-->│Pull Request│-->│  Review  ││
│  │          │   │          │   │          │   │          │   │          ││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘│
└───────────────────────────────────────┬─────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Integração Contínua                               │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │   Lint   │-->│  Testes  │-->│Análise de │-->│  Build   │-->│Publicação││
│  │          │   │Unitários │   │ Segurança │   │          │   │de Artefatos││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘│
└───────────────────────────────────────┬─────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Entrega Contínua                                  │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │Deploy em │-->│  Testes  │-->│Aprovação │-->│Deploy em │-->│  Testes  ││
│  │  Preview │   │Integração│   │          │   │Produção  │   │   E2E    ││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘│
└───────────────────────────────────────┬─────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Operação                                          │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │Monitoram.│<->│   Logs   │<->│  Alertas │<->│Diagnóstico│<->│  Feedback││
│  │          │   │          │   │          │   │          │   │          ││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

## Próximos Passos

1. **Implementação da Infraestrutura Base**: Setup de GitHub Actions, configuração de workflows
2. **Configuração de Ambientes**: Desenvolvimento, staging e produção
3. **Implementação de Testes**: Unitários, integração e end-to-end
4. **Configuração de Monitoramento**: Prometheus, Grafana, alertas
5. **Documentação de Processos**: Guias de contribuição, padrões de código, fluxo de trabalho

Este documento de CI/CD e DevOps foi projetado para atender aos requisitos do GEIH, garantindo qualidade, confiabilidade e agilidade no desenvolvimento através de automação, testes contínuos e monitoramento eficaz.
