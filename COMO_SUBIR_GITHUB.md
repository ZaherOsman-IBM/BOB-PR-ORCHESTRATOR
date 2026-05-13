# 🚀 Como Subir o BOB para o GitHub e Testar

## 📋 Passo a Passo Completo

### 1️⃣ Preparar o BOB

```bash
# Vá para o diretório do BOB
cd ~/Desktop/bob-pr-orchestrator

# Inicialize o Git (se ainda não foi feito)
git init
git add .
git commit -m "Initial commit - BOB PR Orchestrator"
```

### 2️⃣ Criar Repositório no GitHub

1. Acesse https://github.com/new
2. Nome do repositório: `bob-pr-orchestrator`
3. Descrição: `BOB - Build Optimization Bot - Automated code analysis`
4. Deixe como **Public** (ou Private se preferir)
5. **NÃO** marque "Initialize with README"
6. Clique em **Create repository**

### 3️⃣ Subir o BOB para o GitHub

```bash
# Adicione o remote (substitua SEU-USUARIO pelo seu username do GitHub)
git remote add origin https://github.com/SEU-USUARIO/bob-pr-orchestrator.git

# Renomeie a branch para main
git branch -M main

# Faça o push
git push -u origin main
```

### 4️⃣ Preparar o Projeto de Teste

```bash
# Vá para o projeto de teste
cd ~/Desktop/bob-test-project

# Inicialize o Git
git init
git add .
git commit -m "Initial commit - Test project for BOB"
```

### 5️⃣ Criar Repositório do Projeto de Teste

1. Acesse https://github.com/new
2. Nome: `bob-test-project`
3. Descrição: `Test project for BOB analysis`
4. **Public**
5. **NÃO** marque "Initialize with README"
6. Clique em **Create repository**

### 6️⃣ Subir o Projeto de Teste

```bash
# Adicione o remote
git remote add origin https://github.com/SEU-USUARIO/bob-test-project.git

# Renomeie a branch
git branch -M main

# Faça o push
git push -u origin main
```

### 7️⃣ Testar o BOB com um Pull Request

```bash
# Ainda no bob-test-project
# Crie uma branch de teste
git checkout -b test-bob-analysis

# Faça uma pequena mudança
echo "# Testing BOB" >> README.md

# Commit e push
git add README.md
git commit -m "Test: Add comment to trigger BOB"
git push origin test-bob-analysis
```

### 8️⃣ Criar o Pull Request

1. Vá para https://github.com/SEU-USUARIO/bob-test-project
2. Você verá um banner amarelo: **"test-bob-analysis had recent pushes"**
3. Clique em **Compare & pull request**
4. Título: `Test BOB Analysis`
5. Descrição: `Testing BOB automated code analysis`
6. Clique em **Create pull request**

### 9️⃣ Acompanhar a Análise

1. Na página do PR, vá para a aba **Checks**
2. Você verá o workflow **"🤖 BOB Code Analysis"** rodando
3. Aguarde alguns minutos (2-5 minutos)
4. O BOB vai:
   - ✅ Analisar todos os arquivos
   - 💬 Comentar no PR com os resultados
   - 🔴 Bloquear o merge se houver issues críticos

### 🎯 Resultado Esperado

O BOB deve encontrar **8 issues críticos** no `app.py`:
- AWS Access Keys
- Senhas hardcoded
- API Keys expostas
- Tokens em texto plano

O PR será **BLOQUEADO** ❌ e você verá um comentário detalhado.

## 📊 Visualizando os Resultados

### No Pull Request:
- 💬 Comentário do BOB com resumo
- ❌ Check vermelho (bloqueado)
- 📋 Link para o relatório completo

### Nos Artifacts:
1. Vá para **Actions** no repositório
2. Clique no workflow que rodou
3. Role até **Artifacts**
4. Baixe `bob-analysis-report`
5. Abra o `bob-report.json`

## 🔧 Ajustar o Workflow (Opcional)

Se o BOB não encontrar o repositório `bob-pr-orchestrator`, edite o workflow:

```bash
cd ~/Desktop/bob-test-project
```

Edite `.github/workflows/bob-analysis.yml` e mude a linha 23:

```yaml
# De:
repository: ${{ github.repository_owner }}/bob-pr-orchestrator

# Para (substitua SEU-USUARIO):
repository: SEU-USUARIO/bob-pr-orchestrator
```

Depois:
```bash
git add .github/workflows/bob-analysis.yml
git commit -m "Fix BOB repository path"
git push
```

## 🐛 Troubleshooting

### Erro: "Repository not found"

O workflow não conseguiu acessar o repositório do BOB. Soluções:

1. **Certifique-se que o repositório `bob-pr-orchestrator` é público**
2. Ou use a **Opção A** do `SETUP_GITHUB_ONLINE.md` (copiar BOB para dentro do projeto)

### Workflow não está rodando

1. Verifique se o arquivo está em `.github/workflows/bob-analysis.yml`
2. Confirme que o PR é para a branch `main`
3. Veja os logs em **Actions**

### BOB não comenta no PR

Verifique as permissões do workflow. O arquivo já tem:
```yaml
permissions:
  contents: read
  pull-requests: write
```

## 🎉 Próximos Passos

Depois que o BOB funcionar:

1. ✅ Corrija os issues críticos no código
2. 🔄 Faça push das correções
3. 🤖 BOB vai analisar novamente automaticamente
4. ✅ Quando não houver issues críticos, o PR será aprovado

## 💡 Exemplo de Correção

Para corrigir os issues críticos em `app.py`:

```python
# Antes (❌ ERRADO):
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
password = "senha123"

# Depois (✅ CORRETO):
import os
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
password = os.getenv("DB_PASSWORD")
```

Depois:
```bash
git add app.py
git commit -m "Fix: Remove hardcoded credentials"
git push
```

O BOB vai rodar novamente e aprovar! ✅

---

## 📝 Resumo dos Comandos

```bash
# 1. Subir BOB
cd ~/Desktop/bob-pr-orchestrator
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/SEU-USUARIO/bob-pr-orchestrator.git
git branch -M main
git push -u origin main

# 2. Subir projeto de teste
cd ~/Desktop/bob-test-project
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/SEU-USUARIO/bob-test-project.git
git branch -M main
git push -u origin main

# 3. Criar PR de teste
git checkout -b test-bob-analysis
echo "# Testing BOB" >> README.md
git add README.md
git commit -m "Test BOB"
git push origin test-bob-analysis
# Depois crie o PR no GitHub
```

---

**Pronto! Agora você tem o BOB rodando automaticamente em todos os seus PRs! 🚀**