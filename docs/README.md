# BOB - Pull Request Orchestrator and Code Compliance

🤖 **BOB** é um sistema automatizado de análise de Pull Requests e verificação de compliance de código para a IBM.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Políticas de Compliance](#políticas-de-compliance)
- [Integração Slack](#integração-slack)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

BOB automatiza a revisão técnica de Pull Requests, verificando:

- ✅ **Qualidade de Código**: Análise estática para múltiplas linguagens
- 🔒 **Segurança**: Detecção de credenciais, secrets e vulnerabilidades
- 🏗️ **Arquitetura**: Conformidade com padrões (VIPER, MVC, etc.)
- 📚 **Bibliotecas**: Verificação de dependências autorizadas
- 📊 **Métricas**: Complexidade, tamanho de funções, cobertura

## ✨ Funcionalidades

### Análise Multi-Linguagem

- **Swift**: Arquitetura VIPER, memory leaks, force unwrapping
- **Python**: PEP 8, type hints, docstrings, complexidade
- **Java**: Padrões de design, tratamento de exceções
- **JavaScript**: ESLint, async/await, PropTypes

### Verificações de Segurança

- Credenciais hardcoded (passwords, API keys, tokens)
- AWS credentials expostas
- Strings de conexão de banco de dados
- Funções perigosas (eval, exec, pickle)
- Vulnerabilidades conhecidas em bibliotecas

### Notificações Inteligentes

- Mensagens formatadas no Slack
- Menção automática de desenvolvedores e revisores
- Relatórios detalhados com links
- Diferentes canais por severidade

## 🏗️ Arquitetura

```
bob-pr-orchestrator/
├── bob/
│   ├── analyzers/          # Analisadores por linguagem
│   │   ├── base_analyzer.py
│   │   ├── swift_analyzer.py
│   │   ├── python_analyzer.py
│   │   └── analyzer_factory.py
│   ├── compliance/         # Verificações de compliance
│   │   ├── security_checker.py
│   │   ├── architecture_checker.py
│   │   └── library_checker.py
│   ├── reporters/          # Notificações e relatórios
│   │   ├── slack_notifier.py
│   │   └── report_generator.py
│   └── main.py            # Orquestrador principal
├── config/
│   ├── ibm_policies.yaml  # Políticas IBM
│   └── slack_config.yaml  # Configuração Slack
├── .gitlab-ci.yml         # Pipeline GitLab CI/CD
└── requirements.txt       # Dependências Python
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- GitLab (self-hosted ou GitLab.com)
- Slack workspace
- Git

### Passo 1: Clone o Repositório

```bash
git clone <seu-repositorio>
cd bob-pr-orchestrator
```

### Passo 2: Instale Dependências

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Passo 3: Configure Variáveis de Ambiente

Crie um arquivo `.env`:

```bash
# GitLab
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=seu-token-aqui

# Slack
SLACK_BOT_TOKEN=xoxb-seu-token-aqui
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Opcional
BOB_ENV=production
```

## ⚙️ Configuração

### 1. GitLab CI/CD

Adicione o arquivo `.gitlab-ci.yml` ao seu repositório:

```yaml
include:
  - local: 'bob-pr-orchestrator/.gitlab-ci.yml'
```

### 2. Variáveis GitLab

Configure em **Settings > CI/CD > Variables**:

- `SLACK_BOT_TOKEN`: Token do bot Slack
- `SLACK_WEBHOOK_URL`: Webhook URL do Slack

### 3. Políticas IBM

Edite `config/ibm_policies.yaml` para customizar:

```yaml
security:
  block_on_credentials: true
  forbidden_patterns:
    - pattern: '(?i)password\s*=\s*[''"][^''"]+[''"]'
      message: "Senha hardcoded detectada"
      severity: CRITICAL

architecture:
  swift:
    enforce_viper: true
    max_function_lines: 50
```

### 4. Slack

#### Criar Bot Slack

1. Acesse https://api.slack.com/apps
2. Crie novo app
3. Adicione permissões:
   - `chat:write`
   - `chat:write.public`
4. Instale no workspace
5. Copie o Bot Token

#### Mapear Usuários

Edite `config/slack_config.yaml`:

```yaml
user_mapping:
  joao.silva: U01234ABCDE  # GitLab: Slack ID
  maria.santos: U56789FGHIJ
```

Para obter Slack IDs:
```bash
# No Slack, clique no perfil do usuário
# Copie o Member ID
```

## 📖 Uso

### Uso Automático (GitLab CI/CD)

BOB executa automaticamente quando:
1. Um Pull Request é criado
2. Novos commits são adicionados ao PR
3. O PR é atualizado

### Uso Manual

```bash
python -m bob.main \
  --pr-id 123 \
  --project-id 456 \
  --gitlab-url https://gitlab.com \
  --gitlab-token $GITLAB_TOKEN \
  --config config/ibm_policies.yaml \
  --slack-config config/slack_config.yaml \
  --output bob-report.json
```

### Parâmetros

- `--pr-id`: ID do Pull Request
- `--project-id`: ID do projeto GitLab
- `--gitlab-url`: URL do GitLab
- `--gitlab-token`: Token de acesso
- `--config`: Arquivo de políticas
- `--slack-config`: Configuração Slack
- `--output`: Arquivo de saída do relatório

## 🔒 Políticas de Compliance

### Níveis de Severidade

- **CRITICAL** 🔴: Bloqueia PR
- **HIGH** 🟠: Requer atenção imediata
- **MEDIUM** 🟡: Deve ser corrigido
- **LOW** 🟢: Sugestão de melhoria
- **INFO** ℹ️: Informativo

### Regras de Segurança

#### Credenciais Proibidas

```python
# ❌ ERRADO
password = "minha-senha-123"
api_key = "AKIAIOSFODNN7EXAMPLE"

# ✅ CORRETO
password = os.getenv('DB_PASSWORD')
api_key = os.getenv('AWS_API_KEY')
```

#### Strings de Conexão

```python
# ❌ ERRADO
conn_str = "mongodb://user:pass@localhost:27017/db"

# ✅ CORRETO
conn_str = os.getenv('MONGODB_URI')
```

### Regras de Arquitetura

#### Swift VIPER

```swift
// ❌ ERRADO - Lógica de negócio no View
class LoginViewController: UIViewController {
    func login() {
        let user = fetchUserFromAPI()  // ❌
    }
}

// ✅ CORRETO - Lógica no Interactor
class LoginInteractor {
    func login() {
        let user = fetchUserFromAPI()  // ✅
    }
}
```

#### Python

```python
# ❌ ERRADO - Função muito longa
def process_data(data):
    # 100 linhas de código...
    pass

# ✅ CORRETO - Funções menores
def validate_data(data):
    # 10 linhas
    pass

def transform_data(data):
    # 10 linhas
    pass
```

## 💬 Integração Slack

### Formato de Notificação

```
🤖 BOB verificou o Pull Request

📋 PR #1234: Implementar autenticação OAuth
🔗 Link: https://gitlab.com/projeto/merge_requests/1234

👤 Desenvolvedor: @joao.silva
👁️ Revisor: @maria.santos

📊 Resultado da Análise:
• ✅ 13 arquivos sem problemas
• 🔴 2 erros críticos encontrados
• ⚠️ 5 avisos
• 💡 8 sugestões de melhoria

🔴 Erros Críticos (PR bloqueado):
1. Credencial AWS exposta em src/config/aws.py:23
2. Violação arquitetura VIPER em LoginViewController.swift:156

📝 Próximos Passos:
@joao.silva precisa corrigir os erros críticos antes da revisão humana.
```

### Canais Configuráveis

```yaml
channels:
  critical: "#alerts-critical"    # Erros críticos
  security: "#security-alerts"    # Alertas de segurança
  architecture: "#architecture"   # Violações arquiteturais
  general: "#code-reviews"        # Geral
```

## 🐛 Troubleshooting

### BOB não está executando

**Problema**: Pipeline não inicia no PR

**Solução**:
1. Verifique `.gitlab-ci.yml` está no repositório
2. Confirme que o PR está em estado "open"
3. Verifique permissões do GitLab Runner

### Notificações Slack não chegam

**Problema**: BOB analisa mas não notifica

**Solução**:
1. Verifique `SLACK_BOT_TOKEN` está configurado
2. Confirme permissões do bot Slack
3. Teste webhook manualmente:
```bash
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Teste BOB"}'
```

### Falsos Positivos

**Problema**: BOB reporta erros incorretos

**Solução**:
1. Ajuste padrões em `config/ibm_policies.yaml`
2. Adicione exceções específicas
3. Reporte issue para melhorias

### Performance Lenta

**Problema**: Análise demora muito

**Solução**:
1. Limite arquivos analisados
2. Aumente timeout no `.gitlab-ci.yml`
3. Use cache para dependências

## 📞 Suporte

- **Documentação**: `/docs`
- **Issues**: GitLab Issues
- **Slack**: #bob-support
- **Email**: bob-team@ibm.com

## 📄 Licença

Copyright © 2024 IBM Corporation. Todos os direitos reservados.

---

**Desenvolvido com ❤️ pela equipe IBM Development**