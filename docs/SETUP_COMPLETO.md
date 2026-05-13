# 🚀 Setup Completo do BOB - Integração Automática

Este guia mostra como configurar o BOB para funcionar **automaticamente** quando você fizer um Pull Request via terminal.

## 📋 Visão Geral do Fluxo

```
Você faz PR → GitLab detecta → BOB analisa → Slack notifica → Revisor age
     ↓              ↓                ↓              ↓              ↓
  Terminal      Automático      Automático     Automático    Humano
```

## 🎯 Objetivo

Após este setup, quando você executar:

```bash
git push origin feature/minha-feature
# Criar MR no GitLab
```

**BOB automaticamente:**
1. ✅ Detecta o Pull Request
2. 🔍 Analisa todos os arquivos modificados
3. 🔒 Verifica credenciais e vulnerabilidades
4. 💬 Envia notificação no Slack
5. 🚫 Bloqueia PR se houver erros críticos

## 📦 Pré-requisitos

- GitLab (self-hosted ou GitLab.com)
- Slack workspace
- Acesso admin ao repositório
- Python 3.11+ (para testes locais opcionais)

---

## 🔧 PASSO 1: Setup do Repositório GitLab

### 1.1 Adicione BOB ao Seu Repositório

```bash
# No seu repositório existente
cd seu-projeto

# Copie a pasta bob-pr-orchestrator
cp -r /caminho/para/bob-pr-orchestrator .

# Commit
git add bob-pr-orchestrator/
git commit -m "feat: Add BOB PR Orchestrator"
git push origin main
```

### 1.2 Configure o Pipeline GitLab

**Opção A: Incluir no seu .gitlab-ci.yml existente**

Adicione no **início** do seu `.gitlab-ci.yml`:

```yaml
# .gitlab-ci.yml (seu arquivo existente)

# Inclui BOB no pipeline
include:
  - local: 'bob-pr-orchestrator/.gitlab-ci.yml'

# Seus stages existentes
stages:
  - bob-analysis  # BOB roda primeiro
  - test
  - build
  - deploy

# Seus jobs existentes continuam aqui...
```

**Opção B: Criar novo .gitlab-ci.yml (se não tiver)**

```bash
# Copie o arquivo do BOB
cp bob-pr-orchestrator/.gitlab-ci.yml .gitlab-ci.yml

# Commit
git add .gitlab-ci.yml
git commit -m "ci: Configure BOB pipeline"
git push origin main
```

---

## 🔐 PASSO 2: Configurar Tokens e Secrets

### 2.1 Token do GitLab

O token já está disponível automaticamente via `CI_JOB_TOKEN`.
Não precisa configurar nada! ✅

### 2.2 Tokens do Slack

#### A. Criar Bot Slack

1. Acesse: https://api.slack.com/apps
2. Clique em **"Create New App"**
3. Escolha **"From scratch"**
4. Nome: `BOB - PR Analyzer`
5. Workspace: Selecione seu workspace

#### B. Configurar Permissões

1. No menu lateral: **OAuth & Permissions**
2. Em **Scopes**, adicione:
   - `chat:write`
   - `chat:write.public`
3. Clique em **"Install to Workspace"**
4. Autorize o app
5. **Copie o "Bot User OAuth Token"** (começa com `xoxb-`)

#### C. Criar Webhook (Opcional, mas recomendado)

1. No menu lateral: **Incoming Webhooks**
2. Ative: **"Activate Incoming Webhooks"**
3. Clique em **"Add New Webhook to Workspace"**
4. Selecione canal: `#code-reviews` (ou crie um)
5. **Copie a Webhook URL**

### 2.3 Adicionar Variáveis no GitLab

1. No GitLab, vá para: **Settings > CI/CD > Variables**
2. Clique em **"Add Variable"**
3. Adicione as seguintes variáveis:

| Key | Value | Protected | Masked |
|-----|-------|-----------|--------|
| `SLACK_BOT_TOKEN` | `xoxb-seu-token-aqui` | ✅ | ✅ |
| `SLACK_WEBHOOK_URL` | `https://hooks.slack.com/...` | ✅ | ✅ |

**Importante:**
- ✅ Marque "Protected" (apenas branches protegidas)
- ✅ Marque "Masked" (oculta nos logs)
- ❌ NÃO marque "Expand variable reference"

---

## ⚙️ PASSO 3: Configurar Políticas (Opcional)

### 3.1 Editar Políticas IBM

```bash
# Edite o arquivo de configuração
nano bob-pr-orchestrator/config/ibm_policies.yaml
```

**Principais configurações:**

```yaml
security:
  block_on_credentials: true  # Bloqueia se encontrar credenciais
  
architecture:
  python:
    max_function_lines: 30  # Ajuste conforme seu padrão
  
  java:
    max_method_lines: 30
  
  javascript:
    forbid_console_log: true  # Bloqueia console.log
```

### 3.2 Mapear Usuários GitLab → Slack

```bash
# Edite o arquivo Slack
nano bob-pr-orchestrator/config/slack_config.yaml
```

Adicione mapeamento:

```yaml
user_mapping:
  # gitlab_username: slack_user_id
  joao.silva: U01234ABCDE
  maria.santos: U56789FGHIJ
```

**Como obter Slack User ID:**
1. No Slack, clique no perfil do usuário
2. Clique em "..." (mais opções)
3. Copie o "Member ID"

### 3.3 Commit das Configurações

```bash
git add bob-pr-orchestrator/config/
git commit -m "config: Customize BOB policies"
git push origin main
```

---

## 🧪 PASSO 4: Testar a Integração

### 4.1 Criar Branch de Teste

```bash
# Crie uma nova branch
git checkout -b test/bob-integration

# Adicione um arquivo com problema proposital
cat > test_file.py << 'EOF'
# Arquivo de teste para BOB
password = "senha123"  # BOB vai detectar isso!
api_key = "AKIAIOSFODNN7EXAMPLE"  # E isso também!

def funcao_longa():
    # Função com muitas linhas para testar
    x = 1
    y = 2
    # ... (adicione mais linhas se quiser)
    return x + y
EOF

# Commit e push
git add test_file.py
git commit -m "test: Add file to test BOB"
git push origin test/bob-integration
```

### 4.2 Criar Merge Request

**Via GitLab Web:**
1. Vá para: **Merge Requests > New merge request**
2. Source branch: `test/bob-integration`
3. Target branch: `main`
4. Clique em **"Create merge request"**

**Via Terminal (se tiver GitLab CLI):**
```bash
glab mr create \
  --source-branch test/bob-integration \
  --target-branch main \
  --title "Test: BOB Integration" \
  --description "Testing BOB automatic analysis"
```

### 4.3 Observar BOB em Ação

**O que vai acontecer:**

1. **GitLab Pipeline inicia** (automático)
   - Vá para: **CI/CD > Pipelines**
   - Veja o job `bob-pr-check` executando

2. **BOB analisa** (1-5 minutos)
   - Detecta credenciais no `test_file.py`
   - Gera relatório

3. **Slack notifica** (automático)
   - Mensagem aparece no canal configurado
   - Menciona você e o revisor
   - Lista erros encontrados

4. **Pipeline falha** (se houver erros críticos)
   - PR fica bloqueado
   - Não pode fazer merge

**Exemplo de notificação Slack:**

```
🤖 BOB verificou o Pull Request

📋 PR #123: Test: BOB Integration
🔗 Link: https://gitlab.com/projeto/merge_requests/123

👤 Desenvolvedor: @seu.usuario
👁️ Revisor: @revisor

📊 Resultado:
• 🔴 2 erros críticos
• ⚠️ 1 aviso

🔴 Erros Críticos (PR bloqueado):
1. Senha hardcoded em test_file.py:2
2. AWS Key detectada em test_file.py:3

📝 Próximos Passos:
@seu.usuario precisa corrigir os erros críticos.
```

---

## ✅ PASSO 5: Uso Normal (Dia a Dia)

Após o setup, seu fluxo normal será:

```bash
# 1. Crie sua feature
git checkout -b feature/nova-funcionalidade

# 2. Desenvolva normalmente
# ... edite arquivos ...

# 3. Commit e push
git add .
git commit -m "feat: Implementar nova funcionalidade"
git push origin feature/nova-funcionalidade

# 4. Crie MR no GitLab (web ou CLI)
# BOB analisa AUTOMATICAMENTE!

# 5. Se BOB aprovar:
#    ✅ Revisor humano pode revisar
#    ✅ Pode fazer merge

# 6. Se BOB bloquear:
#    ❌ Corrija os erros
#    ❌ Push novamente
#    ❌ BOB analisa de novo
```

**Você NÃO precisa:**
- ❌ Executar BOB manualmente
- ❌ Rodar scripts
- ❌ Configurar nada por PR
- ❌ Lembrar de analisar

**BOB faz TUDO automaticamente!** 🤖

---

## 🔍 Verificar se Está Funcionando

### Checklist de Validação

Execute estes comandos para verificar:

```bash
# 1. Verificar se BOB está no repositório
ls -la bob-pr-orchestrator/
# Deve mostrar: bob/, config/, .gitlab-ci.yml, etc.

# 2. Verificar pipeline configurado
cat .gitlab-ci.yml | grep bob-analysis
# Deve mostrar: - bob-analysis

# 3. Verificar variáveis no GitLab
# Vá para: Settings > CI/CD > Variables
# Deve ter: SLACK_BOT_TOKEN e SLACK_WEBHOOK_URL
```

### Logs do Pipeline

Para ver o que BOB está fazendo:

1. GitLab: **CI/CD > Pipelines**
2. Clique no pipeline do seu MR
3. Clique no job `bob-pr-check`
4. Veja os logs em tempo real

**Exemplo de log:**

```
🤖 BOB iniciando análise do Pull Request #123...
📁 Arquivos modificados: 3
🔍 Analisando: src/app.py
  ✓ Usando: PythonAnalyzer
  📊 5 issues encontrados
🔍 Analisando: src/utils.java
  ✓ Usando: JavaAnalyzer
  📊 3 issues encontrados
📊 RESUMO: 8 issues (2 críticos)
🔴 PR BLOQUEADO - Erros críticos encontrados!
❌ Análise concluída com ERROS
```

---

## 🐛 Troubleshooting

### BOB não está executando

**Problema:** Pipeline não inicia quando crio MR

**Soluções:**
```bash
# 1. Verifique se .gitlab-ci.yml existe
ls -la .gitlab-ci.yml

# 2. Verifique sintaxe do YAML
cat .gitlab-ci.yml | python -m yaml

# 3. Verifique se GitLab Runner está ativo
# GitLab: Settings > CI/CD > Runners
```

### Notificação Slack não chega

**Problema:** BOB analisa mas não notifica

**Soluções:**
1. Verifique tokens no GitLab (Settings > CI/CD > Variables)
2. Teste webhook manualmente:
```bash
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Teste BOB"}'
```
3. Verifique permissões do bot Slack

### Pipeline falha com erro

**Problema:** Job `bob-pr-check` falha

**Soluções:**
1. Veja logs completos no GitLab
2. Verifique se `requirements.txt` está correto
3. Teste localmente:
```bash
cd bob-pr-orchestrator
pip install -r requirements.txt
python test_bob.py
```

---

## 📊 Métricas e Monitoramento

### Ver Estatísticas

```bash
# Quantos PRs BOB analisou
# GitLab: Analytics > CI/CD Analytics

# Taxa de bloqueio
# Conte PRs bloqueados vs aprovados

# Tipos de issues mais comuns
# Analise relatórios JSON salvos
```

### Relatórios Salvos

BOB salva relatórios em:
- **GitLab Artifacts**: Disponível por 30 dias
- **Formato**: JSON, HTML, XML (JUnit)

Para baixar:
1. GitLab: **CI/CD > Pipelines**
2. Clique no pipeline
3. Clique em **"Browse"** nos artifacts
4. Baixe `bob-report.json`

---

## 🎓 Resumo do Fluxo Completo

```
┌─────────────────────────────────────────────────────────┐
│ 1. VOCÊ: git push origin feature/minha-feature         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 2. VOCÊ: Cria Merge Request no GitLab                  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 3. GITLAB: Detecta MR, inicia pipeline automaticamente │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 4. BOB: Analisa arquivos modificados (1-5 min)         │
│    - Verifica credenciais                               │
│    - Analisa qualidade de código                        │
│    - Verifica compliance IBM                            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 5. BOB: Envia notificação Slack automaticamente        │
│    - Menciona desenvolvedor e revisor                   │
│    - Lista issues encontrados                           │
│    - Indica se PR está bloqueado                        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 6. DECISÃO:                                             │
│    ✅ Sem erros críticos → Revisor pode revisar         │
│    ❌ Com erros críticos → Você deve corrigir           │
└─────────────────────────────────────────────────────────┘
```

---

## 📞 Suporte

- 📧 Email: bob-team@ibm.com
- 💬 Slack: #bob-support
- 🐛 Issues: GitLab Issues

---

**Pronto! BOB agora funciona automaticamente em todos os seus Pull Requests! 🚀**