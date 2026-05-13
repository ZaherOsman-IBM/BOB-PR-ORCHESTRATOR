# 🧪 Guia de Testes do BOB

Este guia mostra como testar o BOB localmente antes de usar em produção.

## 📋 Índice

- [Teste Local Rápido](#teste-local-rápido)
- [Arquivos de Teste](#arquivos-de-teste)
- [Interpretando Resultados](#interpretando-resultados)
- [Teste com GitLab](#teste-com-gitlab)

## 🚀 Teste Local Rápido

### 1. Instale Dependências

```bash
cd bob-pr-orchestrator
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Execute o Script de Teste

```bash
python test_bob.py
```

### 3. Veja os Resultados

O script irá:
- ✅ Analisar arquivos de teste em `test_samples/`
- 📊 Mostrar issues encontrados
- 💾 Gerar relatório `bob-test-report.json`
- ✅/❌ Indicar se PR seria aprovado ou bloqueado

## 📁 Arquivos de Teste

### test_python.py
Testa análise Python com:
- 🔴 Credenciais hardcoded (CRÍTICO)
- 🟡 Função muito longa
- 🟢 Falta de docstrings
- 🟢 Falta de type hints

### test_java.java
Testa análise Java com:
- 🔴 Senha e API key expostas (CRÍTICO)
- 🟡 Método muito longo
- 🟡 Catch genérico e vazio
- 🟢 APIs deprecated

### test_react.tsx
Testa análise React/TypeScript com:
- 🟡 console.log em produção
- 🟡 useEffect sem dependências
- 🟡 Lista sem keys
- 🟢 Uso de 'any'

## 📊 Exemplo de Saída

```
============================================================
                  🤖 BOB - Teste Local de Análise                  
============================================================

📋 Carregando configuração: config/ibm_policies.yaml
✓ Configuração carregada com sucesso

============================================================
                    🔍 ANÁLISE DE ARQUIVOS                    
============================================================

🔍 Analisando: test_samples/test_python.py
   ✓ Usando: PythonAnalyzer
   📊 8 issues encontrados
   📝 70 linhas analisadas

🔍 Analisando: test_samples/test_java.java
   ✓ Usando: JavaAnalyzer
   📊 12 issues encontrados
   📝 96 linhas analisadas

🔍 Analisando: test_samples/test_react.tsx
   ✓ Usando: JavaScriptAnalyzer
   📊 10 issues encontrados
   📝 92 linhas analisadas

============================================================
                    📊 RESUMO CONSOLIDADO                    
============================================================

📁 Arquivos analisados: 3
📝 Linhas de código: 258
📊 Total de issues: 30

  🔴 Críticos: 4
  🟠 Altos: 6
  🟡 Médios: 12
  🟢 Baixos: 8
  ℹ️  Informativos: 0

============================================================
🔴 ISSUES CRÍTICOS (Bloqueariam PR)
============================================================

1. 🔴 [CRITICAL] Senha hardcoded detectada
   📁 test_samples/test_python.py:8
   📝 Padrão de segurança violado
   💡 Remova a credencial e use um gerenciador de secrets

2. 🔴 [CRITICAL] AWS Access Key ID detectada
   📁 test_samples/test_python.py:9
   📝 Credencial AWS exposta no código
   💡 Use AWS Secrets Manager ou variáveis de ambiente

3. 🔴 [CRITICAL] Senha hardcoded detectada
   📁 test_samples/test_java.java:13
   📝 Padrão de segurança violado
   💡 Remova a credencial e use um gerenciador de secrets

4. 🔴 [CRITICAL] AWS Access Key ID detectada
   📁 test_samples/test_java.java:14
   📝 Credencial AWS exposta no código
   💡 Use AWS Secrets Manager ou variáveis de ambiente

============================================================
❌ PR SERIA BLOQUEADO - Erros críticos encontrados!
============================================================

💾 Relatório salvo em: bob-test-report.json
```

## 🔍 Interpretando Resultados

### Severidades

| Emoji | Severidade | Ação |
|-------|-----------|------|
| 🔴 | CRITICAL | **Bloqueia PR** - Deve ser corrigido |
| 🟠 | HIGH | Requer atenção imediata |
| 🟡 | MEDIUM | Deve ser corrigido |
| 🟢 | LOW | Sugestão de melhoria |
| ℹ️ | INFO | Informativo |

### Decisão do BOB

- **✅ PR APROVADO**: Sem erros críticos, pode prosseguir
- **❌ PR BLOQUEADO**: Erros críticos encontrados, precisa correção

## 📝 Relatório JSON

O arquivo `bob-test-report.json` contém:

```json
{
  "total_files": 3,
  "total_issues": 30,
  "issues": [
    {
      "file_path": "test_samples/test_python.py",
      "line_number": 8,
      "severity": "CRITICAL",
      "category": "security",
      "message": "Senha hardcoded detectada",
      "description": "Padrão de segurança violado",
      "suggestion": "Remova a credencial e use secrets manager"
    }
  ]
}
```

## 🧪 Teste com GitLab

### 1. Crie Repositório de Teste

```bash
git init test-repo
cd test-repo
cp -r ../bob-pr-orchestrator .
git add .
git commit -m "Add BOB"
git push
```

### 2. Configure Variáveis

No GitLab: **Settings > CI/CD > Variables**

```
SLACK_BOT_TOKEN=xoxb-seu-token
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

### 3. Crie Pull Request de Teste

```bash
git checkout -b test-pr
cp bob-pr-orchestrator/test_samples/test_python.py src/
git add src/test_python.py
git commit -m "Test: Add file with issues"
git push origin test-pr
```

### 4. Crie Merge Request

No GitLab:
1. Vá para **Merge Requests > New merge request**
2. Source: `test-pr`, Target: `main`
3. Crie o MR

### 5. Observe BOB em Ação

- Pipeline iniciará automaticamente
- BOB analisará os arquivos
- Notificação chegará no Slack
- PR será bloqueado se houver erros críticos

## 🔧 Customizando Testes

### Adicionar Novo Arquivo de Teste

```bash
# Crie arquivo com problemas propositais
cat > test_samples/test_custom.py << 'EOF'
# Seu código de teste aqui
password = "teste123"  # Será detectado!
EOF

# Adicione ao test_bob.py
# Edite a lista test_files
```

### Ajustar Severidades

Edite `config/ibm_policies.yaml`:

```yaml
security:
  block_on_credentials: false  # Não bloqueia por credenciais
  
code_quality:
  max_complexity: 20  # Aumenta limite de complexidade
```

## 📊 Métricas de Teste

Execute múltiplas vezes para validar:

```bash
# Teste 10 vezes
for i in {1..10}; do
  echo "Teste $i"
  python test_bob.py
done
```

## 🐛 Troubleshooting

### Erro: Module not found

```bash
# Certifique-se de estar no diretório correto
cd bob-pr-orchestrator

# Reinstale dependências
pip install -r requirements.txt
```

### Erro: Config not found

```bash
# Verifique se o arquivo existe
ls config/ibm_policies.yaml

# Se não existir, copie do exemplo
cp config/ibm_policies.yaml.example config/ibm_policies.yaml
```

### Nenhum Issue Detectado

- Verifique se os arquivos de teste existem
- Confirme que as regras estão ativas no config
- Teste com arquivo simples primeiro

## ✅ Checklist de Teste

Antes de usar em produção:

- [ ] Teste local executou sem erros
- [ ] Todos os analisadores funcionaram
- [ ] Issues críticos foram detectados
- [ ] Relatório JSON foi gerado
- [ ] Configurações customizadas funcionam
- [ ] Teste no GitLab passou
- [ ] Notificação Slack chegou
- [ ] PR foi bloqueado corretamente

## 📞 Suporte

Problemas nos testes?
- 📧 Email: bob-team@ibm.com
- 💬 Slack: #bob-support
- 🐛 Issues: GitLab Issues

---

**Bons testes! 🚀**