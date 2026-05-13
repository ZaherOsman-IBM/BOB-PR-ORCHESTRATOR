# 📋 Políticas IBM e Integração Slack - BOB

Este documento explica **todas as políticas** que o BOB verifica e **como funciona** a integração com Slack.

---

## 🔒 POLÍTICAS DE SEGURANÇA

### 1. Credenciais Hardcoded (CRÍTICO - Bloqueia PR)

BOB detecta automaticamente:

#### Senhas
```python
# ❌ BOB BLOQUEIA
password = "senha123"
passwd = "admin123"
pwd = "secret"
```

#### API Keys
```javascript
// ❌ BOB BLOQUEIA
const apiKey = "sk-1234567890abcdef"
const api_key = "AIzaSyD..."
```

#### Tokens e Secrets
```java
// ❌ BOB BLOQUEIA
String token = "ghp_abc123xyz"
String secret = "my-secret-key"
```

#### AWS Credentials
```python
# ❌ BOB BLOQUEIA
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
```

#### Tokens de Autorização
```swift
// ❌ BOB BLOQUEIA
let bearer = "Bearer eyJhbGciOiJIUzI1NiIs..."
```

#### Strings de Conexão de Banco
```python
# ❌ BOB BLOQUEIA
MONGO_URI = "mongodb://user:pass@localhost:27017/db"
POSTGRES_URI = "postgres://user:pass@localhost:5432/db"
```

### 2. Gerenciadores de Secrets Aprovados

✅ **Use apenas estes:**
- IBM Cloud Secrets Manager
- HashiCorp Vault
- AWS Secrets Manager

```python
# ✅ BOB APROVA
from ibm_secrets_manager import SecretsManager
password = secrets_manager.get_secret('db-password')
```

---

## 🏗️ POLÍTICAS DE ARQUITETURA

### Swift/iOS

```yaml
Padrões Obrigatórios: VIPER ou MVVM
Max Linhas por Arquivo: 400
Max Linhas por Função: 50
Max Linhas por Classe: 350
Protocolos: Obrigatório
```

**Exemplo:**
```swift
// ❌ BOB ALERTA - Função muito longa (>50 linhas)
func processData() {
    // 100 linhas de código...
}

// ✅ BOB APROVA
protocol ViewProtocol: AnyObject {
    func showData(_ data: String)
}
```

### Java

```yaml
Padrões: MVC, MVVM, Clean Architecture
Max Linhas por Classe: 500
Max Linhas por Método: 30
Interfaces: Obrigatório
Proibido: God Class, Singleton abuse
```

**Exemplo:**
```java
// ❌ BOB ALERTA - Método muito longo
public void processOrder() {
    // 50 linhas de código...
}

// ✅ BOB APROVA
public interface OrderService {
    void processOrder(Order order);
}
```

### Python

```yaml
PEP 8: Obrigatório
Max Linhas por Função: 30
Max Linhas por Classe: 300
Type Hints: Obrigatório
Docstrings: Obrigatório
```

**Exemplo:**
```python
# ❌ BOB ALERTA - Sem type hints e docstring
def calculate_total(items):
    return sum(items)

# ✅ BOB APROVA
def calculate_total(items: List[float]) -> float:
    """
    Calcula o total de uma lista de valores.
    
    Args:
        items: Lista de valores numéricos
        
    Returns:
        Soma total dos valores
    """
    return sum(items)
```

### JavaScript/TypeScript/React

```yaml
Max Linhas por Componente: 300
Max Linhas por Função: 25
PropTypes: Obrigatório (React)
console.log: Proibido em produção
Async/Await: Preferir sobre Promises
```

**Exemplo React:**
```typescript
// ❌ BOB ALERTA - Sem PropTypes, com console.log
const UserCard = ({ name, email }) => {
    console.log(name); // Proibido!
    return <div>{name}</div>;
}

// ✅ BOB APROVA
interface UserCardProps {
    name: string;
    email: string;
}

const UserCard: React.FC<UserCardProps> = ({ name, email }) => {
    return <div>{name}</div>;
}
```

**React Hooks:**
```javascript
// ❌ BOB ALERTA - useEffect sem dependências
useEffect(() => {
    fetchData();
});

// ✅ BOB APROVA
useEffect(() => {
    fetchData();
}, [userId]);
```

---

## 📚 POLÍTICAS DE BIBLIOTECAS

### Bibliotecas Aprovadas

#### Python
✅ requests, flask, django, fastapi, sqlalchemy, pandas, numpy, pytest

#### Swift
✅ Alamofire, SwiftyJSON, Kingfisher, SnapKit, RxSwift

#### Java
✅ spring-boot, hibernate, junit, mockito, lombok, slf4j

#### JavaScript
✅ react, vue, angular, axios, lodash, jest, typescript, eslint

### Bibliotecas Proibidas

❌ **Python:** `eval`, `exec`, `pickle`, `yaml.load` (usar `yaml.safe_load`)
❌ **Qualquer:** Bibliotecas com vulnerabilidades conhecidas

**Exemplo:**
```python
# ❌ BOB BLOQUEIA - Função perigosa
eval(user_input)  # CRÍTICO!

# ✅ BOB APROVA
import yaml
data = yaml.safe_load(file)
```

---

## 📊 POLÍTICAS DE QUALIDADE DE CÓDIGO

### Complexidade

```yaml
Complexidade Ciclomática Máxima: 10
Cobertura de Testes Mínima: 80%
Documentação: Obrigatória
```

### Métricas

```yaml
Max Parâmetros por Função: 5
Max Blocos Aninhados: 4
Max Return Statements: 3
```

**Exemplo:**
```python
# ❌ BOB ALERTA - Muitos parâmetros
def create_user(name, email, age, address, phone, city, state, zip):
    pass

# ✅ BOB APROVA
def create_user(user_data: UserData):
    pass
```

### Nomenclatura

| Linguagem | Classes | Funções/Métodos | Variáveis | Constantes |
|-----------|---------|-----------------|-----------|------------|
| Swift | PascalCase | camelCase | camelCase | UPPER_SNAKE_CASE |
| Java | PascalCase | camelCase | camelCase | UPPER_SNAKE_CASE |
| Python | PascalCase | snake_case | snake_case | UPPER_SNAKE_CASE |
| JavaScript | PascalCase | camelCase | camelCase | UPPER_SNAKE_CASE |

---

## 🔀 POLÍTICAS DE GIT

### Mensagens de Commit

```yaml
Tamanho Mínimo: 10 caracteres
Referência a Issue: Obrigatória
Padrão: ^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+
```

**Exemplos:**
```bash
# ❌ BOB ALERTA
git commit -m "fix bug"

# ✅ BOB APROVA
git commit -m "fix(auth): corrige validação de token #123"
git commit -m "feat(api): adiciona endpoint de usuários #456"
```

### Nomenclatura de Branches

```yaml
Padrão: ^(feature|bugfix|hotfix|release)/.+
```

**Exemplos:**
```bash
# ❌ BOB ALERTA
git checkout -b minha-feature

# ✅ BOB APROVA
git checkout -b feature/adicionar-login
git checkout -b bugfix/corrigir-validacao
git checkout -b hotfix/security-patch
```

### Tamanho de PR

```yaml
Max Arquivos Modificados: 50
Max Linhas Modificadas: 1000
```

---

## 💬 INTEGRAÇÃO COM SLACK

### Como Funciona

```
┌─────────────────────────────────────────────────────────┐
│ 1. BOB analisa PR e encontra issues                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 2. BOB classifica severidade:                           │
│    • CRITICAL → Canal #alerts-critical                  │
│    • HIGH/MEDIUM → Canal #code-reviews                  │
│    • Segurança → Canal #security-alerts                 │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 3. BOB formata mensagem com:                            │
│    • Link do PR                                         │
│    • Desenvolvedor e Revisor                            │
│    • Resumo de issues                                   │
│    • Lista detalhada de problemas                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 4. BOB envia para Slack via:                            │
│    • Webhook URL (mensagens simples)                    │
│    • Bot Token (mensagens ricas com menções)            │
└─────────────────────────────────────────────────────────┘
```

### Configuração de Tokens

#### 1. Webhook URL (Básico)

```bash
# No GitLab: Settings > CI/CD > Variables
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T00/B00/XXX"
```

**Usado para:** Enviar mensagens simples ao canal

#### 2. Bot Token (Avançado)

```bash
# No GitLab: Settings > CI/CD > Variables
SLACK_BOT_TOKEN = "xoxb-seu-token-aqui"
```

**Usado para:**
- Mencionar usuários (@usuario)
- Enviar mensagens formatadas
- Usar threads
- Adicionar reações

### Canais por Tipo

```yaml
Erros Críticos → #alerts-critical
Segurança → #security-alerts
Arquitetura → #architecture-reviews
Geral → #code-reviews
```

### Formato de Mensagem

#### PR Bloqueado (Erros Críticos)

```
🔴 Pull Request Bloqueado

📋 PR #123: feat: Adicionar autenticação
🔗 https://gitlab.com/projeto/merge_requests/123

👤 Desenvolvedor: @joao.silva
👁️ Revisor: @maria.santos

📊 Resultado:
• 🔴 2 erros críticos
• ⚠️ 3 avisos

🔴 Erros Críticos (PR bloqueado):
1. [CRITICAL] Senha hardcoded em src/auth.py:15
   password = "admin123"
   
2. [CRITICAL] AWS Key detectada em config/aws.py:8
   AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

⚠️ Avisos:
1. [HIGH] Função muito longa em src/utils.py:45 (80 linhas)
2. [MEDIUM] Falta docstring em src/models.py:12
3. [MEDIUM] console.log em src/app.js:34

📝 Próximos Passos:
@joao.silva precisa corrigir os 2 erros críticos antes do merge.
```

#### PR com Avisos

```
⚠️ Pull Request com Avisos

📋 PR #124: refactor: Melhorar performance
🔗 https://gitlab.com/projeto/merge_requests/124

👤 Desenvolvedor: @maria.santos
👁️ Revisor: @joao.silva

📊 Resultado:
• ⚠️ 5 avisos
• ℹ️ 2 sugestões

⚠️ Avisos:
1. [HIGH] Complexidade alta em src/processor.py:23 (CC=15)
2. [MEDIUM] Falta type hints em src/utils.py:45
...

💡 Sugestões:
1. Considere dividir a função em funções menores
2. Adicione testes unitários

✅ PR pode ser revisado por @joao.silva
```

#### PR Aprovado

```
✅ Pull Request Aprovado pelo BOB

📋 PR #125: docs: Atualizar README
🔗 https://gitlab.com/projeto/merge_requests/125

👤 Desenvolvedor: @joao.silva
👁️ Revisor: @maria.santos

📊 Resultado:
• ✅ Nenhum problema encontrado
• 📁 3 arquivos analisados

🎉 Excelente trabalho! PR pronto para revisão humana.
```

### Mapeamento de Usuários

Para mencionar usuários no Slack, configure o mapeamento:

```yaml
# config/slack_config.yaml
user_mapping:
  # gitlab_username: slack_user_id
  joao.silva: U01234ABCDE
  maria.santos: U56789FGHIJ
```

**Como obter Slack User ID:**
1. No Slack, clique no perfil do usuário
2. Clique em "..." (mais opções)
3. Copie o "Member ID" (ex: U01234ABCDE)

### Notificações por Severidade

| Severidade | Notifica? | Menciona Dev | Menciona Revisor | Menciona Canal |
|------------|-----------|--------------|------------------|----------------|
| CRITICAL | ✅ Sim | ✅ Sim | ✅ Sim | ✅ Sim (@channel) |
| HIGH | ✅ Sim | ✅ Sim | ❌ Não | ❌ Não |
| MEDIUM | ✅ Sim | ❌ Não | ❌ Não | ❌ Não |
| LOW | ❌ Não | ❌ Não | ❌ Não | ❌ Não |

### Emojis Personalizados

```yaml
🤖 Bot
🔴 Crítico
⚠️ Aviso
ℹ️ Info
✅ Sucesso
🔒 Segurança
🏗️ Arquitetura
📊 Qualidade
💡 Sugestão
```

---

## 🎯 Resumo das Políticas

### Bloqueiam PR (CRITICAL)

1. ❌ Credenciais hardcoded
2. ❌ API Keys expostas
3. ❌ AWS Credentials
4. ❌ Strings de conexão de banco
5. ❌ Uso de `eval`/`exec`
6. ❌ Bibliotecas proibidas

### Alertam mas não bloqueiam (HIGH/MEDIUM)

1. ⚠️ Funções muito longas
2. ⚠️ Complexidade alta
3. ⚠️ Falta de documentação
4. ⚠️ Falta de type hints
5. ⚠️ console.log em produção
6. ⚠️ Nomenclatura incorreta
7. ⚠️ Arquitetura não seguida

### Sugestões (LOW/INFO)

1. 💡 Melhorias de código
2. 💡 Otimizações
3. 💡 Boas práticas

---

## 🔧 Customização

Todas as políticas são configuráveis em:
- **`config/ibm_policies.yaml`** - Políticas de código
- **`config/slack_config.yaml`** - Configuração Slack

**Exemplo de customização:**

```yaml
# Aumentar limite de linhas para Python
python:
  max_function_lines: 50  # Era 30

# Desabilitar verificação de console.log
javascript:
  forbid_console_log: false  # Era true

# Adicionar novo padrão proibido
security:
  forbidden_patterns:
    - pattern: 'TODO|FIXME'
      message: "Remova TODOs antes do merge"
      severity: MEDIUM
```

---

## 📞 Suporte

- 📧 Email: bob-team@ibm.com
- 💬 Slack: #bob-support
- 📖 Docs: https://github.com/ZaherOsman-IBM/BOB-PR-ORCHESTRATOR

---

**BOB garante que seu código segue as políticas IBM antes de chegar ao revisor humano!** 🤖✅