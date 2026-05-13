# 🚀 Como Usar o BOB em Qualquer Projeto

## 📋 Visão Geral

O BOB pode analisar **qualquer projeto** que tenha código em:
- 🐍 Python
- 📜 JavaScript / TypeScript
- ☕ Java
- 🍎 Swift
- ⚛️ React

## 🎯 Opção 1: Adicionar BOB a um Projeto Existente (RECOMENDADO)

### Passo 1: Suba o BOB para o GitHub

```bash
cd ~/Desktop/bob-pr-orchestrator
git init
git add .
git commit -m "Initial commit - BOB"
git remote add origin https://github.com/SEU-USUARIO/bob-pr-orchestrator.git
git branch -M main
git push -u origin main
```

### Passo 2: Vá para o SEU projeto

```bash
# Exemplo: se seu projeto está em ~/projetos/meu-app
cd ~/projetos/meu-app

# Ou qualquer outro lugar
cd /caminho/para/seu/projeto
```

### Passo 3: Crie o diretório de workflows

```bash
mkdir -p .github/workflows
```

### Passo 4: Crie o arquivo de workflow

Crie o arquivo `.github/workflows/bob-analysis.yml` com este conteúdo:

```yaml
name: 🤖 BOB Code Analysis

on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches:
      - main
      - master
      - develop

permissions:
  contents: read
  pull-requests: write

jobs:
  bob-analysis:
    name: BOB Analysis
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 Checkout project code
        uses: actions/checkout@v4
        with:
          path: project
          fetch-depth: 0
      
      - name: 📥 Checkout BOB analyzer
        uses: actions/checkout@v4
        with:
          repository: SEU-USUARIO/bob-pr-orchestrator
          path: bob
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: 📦 Install BOB dependencies
        run: |
          cd bob
          pip install -r requirements.txt
      
      - name: 🤖 Run BOB Analysis
        id: bob-check
        run: |
          cd bob
          python3 bob_local_test.py ../project --output ../bob-report.json || echo "BOB_FAILED=true" >> $GITHUB_ENV
        continue-on-error: true
      
      - name: 📊 Upload BOB Report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: bob-analysis-report
          path: bob-report.json
          retention-days: 30
      
      - name: 📝 Comment PR with Results
        if: always()
        uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            
            let reportContent = '## 🤖 BOB Analysis Report\n\n';
            
            try {
              const report = JSON.parse(fs.readFileSync('bob-report.json', 'utf8'));
              const summary = report.summary;
              
              reportContent += `### 📊 Summary\n\n`;
              reportContent += `| Metric | Count |\n`;
              reportContent += `|--------|-------|\n`;
              reportContent += `| 📁 Files analyzed | ${summary.total_files} |\n`;
              reportContent += `| 📝 Lines of code | ${summary.total_lines} |\n`;
              reportContent += `| 📊 Total issues | ${summary.total_issues} |\n\n`;
              
              reportContent += `### 🎯 Issues by Severity\n\n`;
              reportContent += `| Severity | Count |\n`;
              reportContent += `|----------|-------|\n`;
              reportContent += `| 🔴 Critical | ${summary.critical} |\n`;
              reportContent += `| 🟠 High | ${summary.high} |\n`;
              reportContent += `| 🟡 Medium | ${summary.medium} |\n`;
              reportContent += `| 🟢 Low | ${summary.low} |\n\n`;
              
              if (summary.critical > 0) {
                reportContent += `### 🔴 Critical Issues (PR Blocked)\n\n`;
                const criticalIssues = report.issues
                  .filter(i => i.severity === 'CRITICAL')
                  .slice(0, 10);
                
                criticalIssues.forEach((issue, idx) => {
                  reportContent += `${idx + 1}. **${issue.message}**\n`;
                  reportContent += `   - 📄 \`${issue.file_path}:${issue.line_number}\`\n`;
                  if (issue.description) {
                    reportContent += `   - 💡 ${issue.description}\n`;
                  }
                  reportContent += `\n`;
                });
                
                if (summary.critical > 10) {
                  reportContent += `\n_... and ${summary.critical - 10} more critical issues_\n\n`;
                }
                
                reportContent += `\n❌ **This PR is BLOCKED due to ${summary.critical} critical issue(s).**\n`;
              } else {
                reportContent += `\n✅ **No critical issues found!**\n`;
              }
              
            } catch (error) {
              reportContent += `⚠️ Could not parse BOB report: ${error.message}\n`;
            }
            
            reportContent += `\n---\n📋 Full report in workflow artifacts.\n`;
            
            const comments = await github.rest.issues.listComments({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
            });
            
            const bobComment = comments.data.find(c => c.body.includes('🤖 BOB Analysis Report'));
            
            if (bobComment) {
              await github.rest.issues.updateComment({
                comment_id: bobComment.id,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: reportContent
              });
            } else {
              await github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: reportContent
              });
            }
      
      - name: ❌ Fail if Critical Issues Found
        if: env.BOB_FAILED == 'true'
        run: |
          echo "❌ BOB found critical issues. PR is blocked."
          exit 1
```

**IMPORTANTE:** Substitua `SEU-USUARIO` na linha 23 pelo seu username do GitHub!

### Passo 5: Commit e push

```bash
git add .github/workflows/bob-analysis.yml
git commit -m "Add BOB code analysis workflow"
git push
```

### Passo 6: Teste com um PR

```bash
# Crie uma branch de teste
git checkout -b test-bob

# Faça qualquer mudança
echo "# Testing BOB" >> README.md

# Commit e push
git add README.md
git commit -m "Test: Trigger BOB analysis"
git push origin test-bob
```

### Passo 7: Crie o Pull Request no GitHub

1. Vá para o repositório no GitHub
2. Clique em **Compare & pull request**
3. Crie o PR
4. Aguarde o BOB analisar (2-5 minutos)
5. Veja o comentário do BOB! 🤖

## 🎯 Opção 2: BOB Dentro do Projeto (Sem Repositório Separado)

Se você preferir ter o BOB dentro do próprio projeto:

### Passo 1: Copie o BOB para seu projeto

```bash
cd seu-projeto

# Copie os arquivos do BOB
cp -r ~/Desktop/bob-pr-orchestrator/bob .
cp -r ~/Desktop/bob-pr-orchestrator/config .
cp ~/Desktop/bob-pr-orchestrator/bob_local_test.py .
cp ~/Desktop/bob-pr-orchestrator/requirements.txt bob-requirements.txt
```

### Passo 2: Crie o workflow simplificado

Crie `.github/workflows/bob-analysis.yml`:

```yaml
name: 🤖 BOB Code Analysis

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  bob-analysis:
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 Checkout
        uses: actions/checkout@v4
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: 📦 Install BOB
        run: pip install -r bob-requirements.txt
      
      - name: 🤖 Run BOB
        run: |
          python3 bob_local_test.py . --output bob-report.json || echo "BOB_FAILED=true" >> $GITHUB_ENV
        continue-on-error: true
      
      - name: 📊 Upload Report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: bob-report
          path: bob-report.json
      
      - name: 📝 Comment on PR
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            let comment = '## 🤖 BOB Analysis\n\n';
            
            try {
              const report = JSON.parse(fs.readFileSync('bob-report.json', 'utf8'));
              const s = report.summary;
              
              comment += `📊 **Summary:** ${s.total_files} files, ${s.total_issues} issues\n\n`;
              comment += `🔴 Critical: ${s.critical} | 🟠 High: ${s.high} | 🟡 Medium: ${s.medium} | 🟢 Low: ${s.low}\n\n`;
              
              if (s.critical > 0) {
                comment += '❌ **PR BLOCKED** - Fix critical issues first.\n';
              } else {
                comment += '✅ **No critical issues!**\n';
              }
            } catch (e) {
              comment += `⚠️ Error: ${e.message}\n`;
            }
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
      
      - name: ❌ Fail if Critical
        if: env.BOB_FAILED == 'true'
        run: exit 1
```

### Passo 3: Commit tudo

```bash
git add .
git commit -m "Add BOB code analysis"
git push
```

## 📝 Exemplos de Projetos

### Projeto Python (Flask/Django)
```bash
cd meu-projeto-python
# Siga os passos acima
# BOB vai analisar todos os .py
```

### Projeto JavaScript (Node/React)
```bash
cd meu-projeto-js
# Siga os passos acima
# BOB vai analisar .js, .jsx, .ts, .tsx
```

### Projeto Java (Spring Boot)
```bash
cd meu-projeto-java
# Siga os passos acima
# BOB vai analisar todos os .java
```

### Projeto Mobile (Swift/iOS)
```bash
cd meu-app-ios
# Siga os passos acima
# BOB vai analisar todos os .swift
```

## 🔍 O que o BOB Detecta

### 🔴 Issues Críticos (Bloqueiam PR):
- AWS Keys hardcoded
- Senhas em texto plano
- API Keys expostas
- Tokens/Secrets no código
- Credenciais de banco de dados

### 🟠 Issues Altos:
- Vulnerabilidades de segurança
- Código duplicado extenso
- Funções muito complexas

### 🟡 Issues Médios:
- Funções muito longas
- Falta de documentação
- Padrões de código não seguidos

### 🟢 Issues Baixos:
- Sugestões de melhoria
- Otimizações possíveis
- Convenções de nomenclatura

## 🎨 Customizar Regras

Edite `config/ibm_policies.yaml` para ajustar as regras:

```yaml
security:
  block_on_credentials: true  # Bloqueia se encontrar credenciais
  
architecture:
  python:
    max_function_lines: 50    # Máximo de linhas por função
    require_docstrings: true  # Exige docstrings
```

## 💡 Dicas

1. **Repositório Privado?** Use a Opção 2 (BOB dentro do projeto)
2. **Múltiplos Projetos?** Use a Opção 1 (BOB separado, reutilizável)
3. **Testar Localmente?** Use `python3 bob_local_test.py .`
4. **Ignorar Arquivos?** BOB já ignora `venv/`, `node_modules/`, `.git/`

## 🐛 Troubleshooting

### "Repository not found"
- Certifique-se que `bob-pr-orchestrator` é público
- Ou use a Opção 2 (BOB dentro do projeto)

### Workflow não roda
- Verifique se o arquivo está em `.github/workflows/`
- Confirme que o PR é para branch `main` ou `master`

### BOB não comenta
- Verifique as permissões no workflow (já incluídas)
- Veja os logs em **Actions** no GitHub

---

## ✅ Checklist Rápido

- [ ] Subi o BOB para o GitHub
- [ ] Criei o workflow no meu projeto
- [ ] Substitui `SEU-USUARIO` pelo meu username
- [ ] Fiz commit e push do workflow
- [ ] Criei um PR de teste
- [ ] BOB comentou no PR! 🎉

---

**Pronto! Agora o BOB vai analisar todos os PRs do seu projeto automaticamente! 🚀**