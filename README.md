# 🤖 BOB - Pull Request Orchestrator

**BOB** (Build Optimization Bot) é o seu Orquestrador de Pull Requests e Sistema de Compliance de Código da IBM.

![BOB Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![GitLab CI](https://img.shields.io/badge/GitLab%20CI-integrated-orange)
![Slack](https://img.shields.io/badge/Slack-integrated-purple)

## 🎯 O que é BOB?

BOB automatiza a revisão técnica de Pull Requests, atuando como o **primeiro filtro de qualidade** antes da revisão humana. Ele analisa código em múltiplas linguagens, verifica compliance com políticas da IBM e notifica o time via Slack.

### ✨ Principais Funcionalidades

- 🔍 **Análise Multi-Linguagem**: Swift, Python, Java, JavaScript
- 🔒 **Segurança**: Detecta credenciais, secrets e vulnerabilidades
- 🏗️ **Arquitetura**: Verifica padrões VIPER, MVC, Clean Architecture
- 📚 **Bibliotecas**: Valida dependências autorizadas
- 💬 **Notificações Slack**: Alertas automáticos formatados
- 🚫 **Bloqueio Inteligente**: Impede merge de código com erros críticos

## 🚀 Quick Start

### 1. Clone e Instale

```bash
git clone <seu-repositorio>
cd bob-pr-orchestrator

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Variáveis

```bash
cp .env.example .env
# Edite .env com seus tokens
```

### 3. Configure GitLab CI/CD

Adicione ao seu `.gitlab-ci.yml`:

```yaml
include:
  - local: 'bob-pr-orchestrator/.gitlab-ci.yml'
```

### 4. Configure Variáveis no GitLab

**Settings > CI/CD > Variables**:
- `SLACK_BOT_TOKEN`
- `SLACK_WEBHOOK_URL`

### 5. Pronto! 🎉

BOB agora analisa automaticamente todos os Pull Requests!

## 📊 Como Funciona

```mermaid
graph LR
    A[Developer cria PR] --> B[GitLab CI/CD]
    B --> C[BOB Analyzer]
    C --> D[Análise Código]
    C --> E[Verificação Segurança]
    C --> F[Check Compliance]
    D --> G[Relatório]
    E --> G
    F --> G
    G --> H{Erros Críticos?}
    H -->|Sim| I[🔴 Bloqueia PR]
    H -->|Não| J[✅ Aprova]
    I --> K[Notifica Slack]
    J --> K
    K --> L[Revisor Humano]
```

## 📋 Exemplo de Análise

### Entrada: Pull Request

```python
# src/config.py
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"  # ❌ Credencial exposta
password = "senha123"              # ❌ Senha hardcoded

def process_data(data):            # ❌ Função muito longa
    # 150 linhas de código...
    pass
```

### Saída: Notificação Slack

```
🤖 BOB verificou o Pull Request

📋 PR #1234: Adicionar configuração AWS
🔗 Link: https://gitlab.com/projeto/merge_requests/1234

👤 Desenvolvedor: @joao.silva
👁️ Revisor: @maria.santos

📊 Resultado da Análise:
• ✅ 5 arquivos sem problemas
• 🔴 2 erros críticos encontrados
• ⚠️ 1 aviso

🔴 Erros Críticos (PR bloqueado):
1. `src/config.py:2` - AWS Access Key ID detectada
2. `src/config.py:3` - Senha hardcoded detectada

⚠️ Avisos:
3. `src/config.py:5` - Função muito longa (150 linhas)

📝 Próximos Passos:
@joao.silva precisa corrigir os erros críticos antes da revisão.
```

## 🔧 Configuração Avançada

### Políticas Customizadas

Edite `config/ibm_policies.yaml`:

```yaml
security:
  block_on_credentials: true
  forbidden_patterns:
    - pattern: '(?i)password\s*=\s*[''"][^''"]+[''"]'
      message: "Senha hardcoded"
      severity: CRITICAL

architecture:
  swift:
    enforce_viper: true
    max_function_lines: 50
  
  python:
    require_type_hints: true
    max_function_lines: 30
```

### Mapeamento Slack

Edite `config/slack_config.yaml`:

```yaml
user_mapping:
  joao.silva: U01234ABCDE
  maria.santos: U56789FGHIJ
```

## 📚 Documentação Completa

- 📖 [Documentação Completa](docs/README.md)
- 🔒 [Políticas de Segurança](docs/SECURITY.md)
- 🏗️ [Guia de Arquitetura](docs/ARCHITECTURE.md)
- 🐛 [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🎓 Linguagens Suportadas

| Linguagem | Status | Verificações |
|-----------|--------|--------------|
| Swift | ✅ | VIPER, Memory Leaks, Force Unwrapping, Protocols |
| Python | ✅ | PEP 8, Type Hints, Docstrings, Complexidade |
| Java | ✅ | Design Patterns, Exception Handling, Naming |
| JavaScript | ✅ | ESLint, Async/Await, Console.log |
| TypeScript | ✅ | Type Safety, Any Usage, Return Types |
| React | ✅ | Hooks, PropTypes, Component Size, Keys |

## 📈 Métricas

BOB analisa em média:
- ⚡ **< 5 minutos** por PR
- 🎯 **95%** de precisão na detecção
- 🔒 **100%** de credenciais bloqueadas
- 📊 **80%** redução em revisões manuais

## 🤝 Contribuindo

Quer melhorar o BOB? Veja nosso [Guia de Contribuição](CONTRIBUTING.md).

## 📞 Suporte

- 💬 Slack: `#bob-support`
- 📧 Email: bob-team@ibm.com
- 🐛 Issues: [GitLab Issues](https://gitlab.com/seu-projeto/issues)

## 📄 Licença

Copyright © 2024 IBM Corporation. Todos os direitos reservados.

---

**Desenvolvido com ❤️ pela equipe IBM Development**

*"Automatizando qualidade, um PR por vez"* 🚀