# 🚀 Configurar BOB no GitHub (Online)

Este guia mostra como configurar o BOB para rodar automaticamente em Pull Requests no GitHub.

## 📋 Pré-requisitos

1. Repositório no GitHub
2. Projeto que você quer analisar (pode ser qualquer projeto Python, JavaScript, etc.)

## 🔧 Passo a Passo

### 1️⃣ Suba o BOB para o GitHub

```bash
# No diretório bob-pr-orchestrator
git init
git add .
git commit -m "Initial commit - BOB PR Orchestrator"

# Crie um repositório no GitHub chamado "bob-pr-orchestrator"
# Depois execute:
git remote add origin https://github.com/SEU-USUARIO/bob-pr-orchestrator.git
git branch -M main
git push -u origin main
```

### 2️⃣ Configure o Projeto que Será Analisado

Você tem duas opções:

#### **Opção A: BOB no mesmo repositório do projeto**

1. Copie o BOB para dentro do seu projeto:
```bash
cd seu-projeto
cp -r ../bob-pr-orchestrator/bob .
cp -r ../bob-pr-orchestrator/config .
cp ../bob-pr-orchestrator/requirements.txt bob-requirements.txt
```

2. Crie o workflow do GitHub Actions:
```bash
mkdir -p .github/workflows
```

3. Crie o arquivo `.github/workflows/bob-check.yml`:

```yaml
name: 🤖 BOB Code Analysis

on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches:
      - main
      - master
      - develop

jobs:
  bob-analysis:
    name: BOB Analysis
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: 📦 Install BOB
        run: |
          pip install -r bob-requirements.txt
      
      - name: 🤖 Run BOB Analysis
        run: |
          python3 bob_local_test.py . --output bob-report.json
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
            
            let comment = '## 🤖 BOB Analysis Report\n\n';
            
            try {
              const report = JSON.parse(fs.readFileSync('bob-report.json', 'utf8'));
              const summary = report.summary;
              
              comment += '### 📊 Summary\n\n';
              comment += `- 📁 Files analyzed: ${summary.total_files}\n`;
              comment += `- 📝 Lines of code: ${summary.total_lines}\n`;
              comment += `- 📊 Total issues: ${summary.total_issues}\n\n`;
              comment += `#### Issues by Severity:\n`;
              comment += `- 🔴 Critical: ${summary.critical}\n`;
              comment += `- 🟠 High: ${summary.high}\n`;
              comment += `- 🟡 Medium: ${summary.medium}\n`;
              comment += `- 🟢 Low: ${summary.low}\n\n`;
              
              if (summary.critical > 0) {
                comment += '### 🔴 Critical Issues\n\n';
                const criticalIssues = report.issues
                  .filter(i => i.severity === 'CRITICAL')
                  .slice(0, 5);
                
                criticalIssues.forEach((issue, idx) => {
                  comment += `${idx + 1}. **${issue.message}**\n`;
                  comment += `   - File: \`${issue.file_path}:${issue.line_number}\`\n`;
                  if (issue.description) {
                    comment += `   - ${issue.description}\n`;
                  }
                  comment += '\n';
                });
                
                if (summary.critical > 5) {
                  comment += `_... and ${summary.critical - 5} more critical issues_\n\n`;
                }
                
                comment += '\n❌ **This PR is blocked due to critical issues.**\n';
              } else {
                comment += '\n✅ **No critical issues found!**\n';
              }
              
            } catch (error) {
              comment += `⚠️ Could not read report: ${error.message}\n`;
            }
            
            comment += '\n---\n';
            comment += '📋 Full report available in workflow artifacts.\n';
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
      
      - name: ❌ Fail if Critical Issues
        run: |
          if [ -f bob-report.json ]; then
            CRITICAL=$(python3 -c "import json; print(json.load(open('bob-report.json'))['summary']['critical'])")
            if [ "$CRITICAL" -gt 0 ]; then
              echo "❌ Found $CRITICAL critical issues"
              exit 1
            fi
          fi
```

4. Copie também o `bob_local_test.py`:
```bash
cp ../bob-pr-orchestrator/bob_local_test.py .
```

5. Commit e push:
```bash
git add .
git commit -m "Add BOB code analysis"
git push
```

#### **Opção B: BOB como repositório separado (Reusável)**

1. Crie um workflow que usa o BOB de outro repositório:

```yaml
name: 🤖 BOB Code Analysis

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  bob-analysis:
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 Checkout project
        uses: actions/checkout@v4
        with:
          path: project
      
      - name: 📥 Checkout BOB
        uses: actions/checkout@v4
        with:
          repository: SEU-USUARIO/bob-pr-orchestrator
          path: bob
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: 📦 Install BOB
        run: |
          cd bob
          pip install -r requirements.txt
      
      - name: 🤖 Run BOB
        run: |
          cd bob
          python3 bob_local_test.py ../project --output ../bob-report.json
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
            let comment = '## 🤖 BOB Analysis Report\n\n';
            
            try {
              const report = JSON.parse(fs.readFileSync('bob-report.json', 'utf8'));
              const summary = report.summary;
              
              comment += `### 📊 Summary\n\n`;
              comment += `- 📁 Files: ${summary.total_files}\n`;
              comment += `- 🔴 Critical: ${summary.critical}\n`;
              comment += `- 🟠 High: ${summary.high}\n`;
              comment += `- 🟡 Medium: ${summary.medium}\n`;
              comment += `- 🟢 Low: ${summary.low}\n\n`;
              
              if (summary.critical > 0) {
                comment += '❌ **PR blocked due to critical issues**\n';
              } else {
                comment += '✅ **No critical issues**\n';
              }
            } catch (error) {
              comment += `⚠️ Error: ${error.message}\n`;
            }
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### 3️⃣ Teste o BOB

1. Crie uma branch de teste:
```bash
git checkout -b test-bob
```

2. Faça uma mudança qualquer:
```bash
echo "# Test" >> README.md
git add README.md
git commit -m "Test BOB"
git push origin test-bob
```

3. Abra um Pull Request no GitHub

4. O BOB vai rodar automaticamente! 🎉

### 4️⃣ Veja os Resultados

Após alguns minutos, você verá:

1. ✅ Check do GitHub Actions (verde ou vermelho)
2. 💬 Comentário do BOB no PR com o resumo
3. 📊 Relatório completo nos artifacts do workflow

## 🎯 Exemplo de Resultado no PR

O BOB vai comentar algo assim:

```
## 🤖 BOB Analysis Report

### 📊 Summary

- 📁 Files analyzed: 5
- 📝 Lines of code: 450
- 📊 Total issues: 12

#### Issues by Severity:
- 🔴 Critical: 2
- 🟠 High: 3
- 🟡 Medium: 5
- 🟢 Low: 2

### 🔴 Critical Issues

1. **AWS Access Key ID detectada**
   - File: `config.py:15`
   - Credencial AWS exposta no código

2. **Senha hardcoded detectada**
   - File: `auth.py:42`
   - Padrão de segurança violado

❌ **This PR is blocked due to critical issues.**

---
📋 Full report available in workflow artifacts.
```

## 🔒 Configurações de Segurança (Opcional)

Se você quiser notificações no Slack:

1. Vá em **Settings > Secrets and variables > Actions**
2. Adicione:
   - `SLACK_BOT_TOKEN`
   - `SLACK_WEBHOOK_URL`

## 🐛 Troubleshooting

### Workflow não está rodando?

1. Verifique se o arquivo está em `.github/workflows/`
2. Confirme que o PR é para branch `main` ou `master`
3. Veja os logs em **Actions** no GitHub

### BOB não encontra arquivos?

Verifique o caminho no comando:
```yaml
python3 bob_local_test.py . --output bob-report.json
```

### Erro de permissão no comentário?

O GitHub Actions precisa de permissão para comentar. Adicione no workflow:

```yaml
permissions:
  contents: read
  pull-requests: write
```

## 📚 Próximos Passos

1. ✅ Configure o workflow
2. 🧪 Teste com um PR
3. 🔧 Ajuste as políticas em `config/ibm_policies.yaml`
4. 📊 Monitore os resultados

## 💡 Dicas

- O BOB roda em **todos os PRs** automaticamente
- Issues críticos **bloqueiam o merge**
- Você pode ver o relatório completo nos artifacts
- Customize as regras editando `config/ibm_policies.yaml`

---

**Pronto! Agora o BOB vai analisar todos os seus PRs automaticamente! 🚀**