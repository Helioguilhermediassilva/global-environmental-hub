# Guia de Publicação no GitHub

Este guia fornece instruções passo a passo para publicar o projeto Global Environmental Intelligence Hub (GEIH) no GitHub e estabelecer um fluxo de trabalho eficiente para desenvolvimento colaborativo.

## 1. Preparação Inicial

Antes de iniciar a publicação, certifique-se de que:

- Você tem uma conta no GitHub (https://github.com)
- Git está instalado em sua máquina local
- Você tem permissões para criar repositórios na organização desejada

## 2. Criação do Repositório no GitHub

1. Acesse sua conta GitHub em https://github.com/Helioguilhermediassilva
2. Clique no botão "+" no canto superior direito e selecione "New repository"
3. Configure o repositório:
   - Nome: `global-environmental-hub`
   - Descrição: "Plataforma de código aberto para monitoramento ambiental e análise preditiva com IA"
   - Visibilidade: Public
   - Inicializar com README: Não (vamos fazer upload do nosso próprio README)
   - Adicione uma licença MIT
4. Clique em "Create repository"

## 3. Configuração Local e Primeiro Commit

```bash
# Navegue até o diretório do projeto
cd /caminho/para/global-environmental-hub

# Inicialize o repositório Git local
git init

# Adicione o repositório remoto
git remote add origin https://github.com/Helioguilhermediassilva/global-environmental-hub.git

# Verifique se .gitignore está configurado corretamente
cat .gitignore

# Adicione todos os arquivos ao staging
git add .

# Faça o commit inicial
git commit -m "Initial commit: Project structure and base implementation"

# Crie e mude para a branch main
git branch -M main

# Envie o código para o GitHub
git push -u origin main
```

## 4. Estrutura de Branches

O projeto segue o modelo GitFlow adaptado:

- **main**: Código estável, pronto para produção
- **develop**: Branch de desenvolvimento, integração de features
- **feature/\***: Desenvolvimento de novas funcionalidades
- **bugfix/\***: Correção de bugs em desenvolvimento
- **hotfix/\***: Correção de bugs críticos em produção
- **release/\***: Preparação para nova versão

Após o commit inicial, crie a branch develop:

```bash
# Criar e mudar para a branch develop
git checkout -b develop

# Enviar a branch develop para o GitHub
git push -u origin develop
```

## 5. Proteção de Branches

Configure proteções para as branches principais:

1. No GitHub, vá para "Settings" > "Branches"
2. Clique em "Add rule"
3. Em "Branch name pattern", digite `main`
4. Marque as seguintes opções:
   - "Require pull request reviews before merging"
   - "Require status checks to pass before merging"
   - "Include administrators"
5. Clique em "Create"
6. Repita o processo para a branch `develop`

## 6. Configuração de GitHub Actions

O projeto já inclui workflows de CI/CD em `.github/workflows/`. Para ativá-los:

1. No GitHub, vá para "Actions"
2. Você verá os workflows disponíveis, clique em "I understand my workflows, go ahead and enable them"

## 7. Fluxo de Trabalho para Novas Funcionalidades

Para desenvolver uma nova funcionalidade:

```bash
# Atualizar a branch develop
git checkout develop
git pull

# Criar uma nova branch de feature
git checkout -b feature/nome-da-funcionalidade

# Desenvolver a funcionalidade...

# Adicionar e commitar as mudanças
git add .
git commit -m "feat: descrição da funcionalidade"

# Enviar a branch para o GitHub
git push -u origin feature/nome-da-funcionalidade
```

Em seguida, crie um Pull Request no GitHub:

1. Vá para o repositório no GitHub
2. Clique em "Pull requests" > "New pull request"
3. Selecione `develop` como base e sua branch de feature como compare
4. Clique em "Create pull request"
5. Adicione título, descrição e solicite revisores
6. Aguarde a revisão e aprovação

## 8. Merge de Pull Requests

Após a aprovação do PR:

1. Clique em "Merge pull request"
2. Selecione "Squash and merge" para manter o histórico limpo
3. Confirme o merge
4. Delete a branch de feature após o merge

## 9. Releases

Para criar uma release:

1. Crie uma branch de release a partir de develop:
   ```bash
   git checkout develop
   git pull
   git checkout -b release/v1.0.0
   ```

2. Faça ajustes finais, atualize versão e documentação
   ```bash
   # Editar arquivos de versão, CHANGELOG, etc.
   git add .
   git commit -m "chore: prepare release v1.0.0"
   ```

3. Envie a branch para o GitHub
   ```bash
   git push -u origin release/v1.0.0
   ```

4. Crie um PR de `release/v1.0.0` para `main`

5. Após aprovação e merge, crie uma tag:
   ```bash
   git checkout main
   git pull
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin v1.0.0
   ```

6. No GitHub, vá para "Releases" > "Draft a new release"
   - Tag: v1.0.0
   - Title: Version 1.0.0
   - Description: Notas da release
   - Publish release

7. Não esqueça de mesclar as mudanças de volta para develop:
   ```bash
   git checkout develop
   git pull
   git merge --no-ff main
   git push
   ```

## 10. Configuração de Colaboradores

Para adicionar colaboradores ao projeto:

1. No GitHub, vá para "Settings" > "Manage access"
2. Clique em "Invite a collaborator"
3. Digite o nome de usuário ou email do colaborador
4. Selecione o nível de permissão apropriado
5. Clique em "Add"

## 11. Documentação e Wiki

O projeto inclui documentação abrangente em `/docs`. Você também pode configurar o Wiki do GitHub:

1. No GitHub, vá para a aba "Wiki"
2. Clique em "Create the first page"
3. Adicione conteúdo inicial, como links para a documentação principal
4. Salve a página

## 12. GitHub Pages (Opcional)

Para publicar a documentação como site:

1. No GitHub, vá para "Settings" > "Pages"
2. Em "Source", selecione "Deploy from a branch"
3. Selecione a branch `main` e a pasta `/docs`
4. Clique em "Save"

## 13. Problemas e Tarefas

Use o sistema de Issues do GitHub para rastrear tarefas:

1. No GitHub, vá para "Issues" > "New issue"
2. Use templates ou crie issues personalizadas
3. Atribua responsáveis, adicione labels e milestones

## 14. Projetos e Quadros Kanban

Para gerenciar o trabalho:

1. No GitHub, vá para "Projects" > "New project"
2. Selecione "Board" como template
3. Configure colunas (To do, In progress, Done)
4. Adicione issues ao quadro

## 15. Manutenção Contínua

Práticas recomendadas para manutenção:

- Mantenha as dependências atualizadas
- Execute testes regularmente
- Revise e atualize a documentação
- Monitore issues e pull requests
- Faça backups regulares do repositório

## 16. Solução de Problemas Comuns

### Conflitos de Merge

```bash
# Quando ocorrer um conflito
git status  # Veja os arquivos com conflito
# Edite os arquivos para resolver os conflitos
git add .  # Adicione os arquivos resolvidos
git commit  # Continue o merge ou rebase
```

### Reverter Mudanças

```bash
# Reverter um commit específico
git revert <commit-hash>

# Reverter o último commit
git revert HEAD
```

### Recuperar Mudanças Perdidas

```bash
# Ver histórico de referências
git reflog

# Recuperar estado anterior
git checkout <ref-hash>
```

## Conclusão

Seguindo este guia, você estabelecerá um fluxo de trabalho eficiente para o desenvolvimento colaborativo do Global Environmental Intelligence Hub. A estrutura de branches, proteções e processos de revisão garantem a qualidade do código e facilitam a colaboração entre múltiplos desenvolvedores.

Para dúvidas ou sugestões sobre este guia, abra uma issue no repositório.
