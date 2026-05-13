# 🚀 Guia Rápido - BOB Local Test

Este guia mostra como testar o BOB localmente sem precisar de GitLab ou GitHub.

## 📋 Pré-requisitos

1. Python 3.11 ou superior
2. Dependências instaladas

## 🔧 Instalação

### 1. Instale as dependências

```bash
# Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

## 🧪 Testando Localmente

### Teste 1: Analisar o próprio projeto BOB

```bash
python bob_local_test.py .
```

Isso vai analisar todos os arquivos Python no diretório atual.

### Teste 2: Analisar um diretório específico

```bash
python bob_local_test.py ../bob-test-project
```

### Teste 3: Analisar apenas arquivos Python

```bash
python bob_local_test.py . --extensions .py
```

### Teste 4: Analisar múltiplas extensões

```bash
python bob_local_test.py . --extensions .py .js .java
```

### Teste 5: Salvar relatório customizado

```bash
python bob_local_test.py . --output meu-relatorio.json
```

## 📊 Entendendo o Resultado

O BOB vai mostrar:

- ✅ **Arquivos analisados**: Quantos arquivos foram verificados
- 📝 **Linhas de código**: Total de linhas analisadas
- 🔴 **Issues Críticos**: Problemas que bloqueiam o código
- 🟠 **Issues Altos**: Problemas importantes
- 🟡 **Issues Médios**: Melhorias recomendadas
- 🟢 **Issues Baixos**: Sugestões menores

### Exemplo de Saída

```
============================================================
🤖 BOB - Análise Local de Código
============================================================

📁 Diretório: .
🔍 Extensões: .py, .js, .java, .swift, .ts, .tsx

📊 Arquivos encontrados: 15

  🔍 Analisando: bob/main.py
    ✅ Sem issues
  🔍 Analisando: bob/analyzers/python_analyzer.py
    ⚠️  3 issues encontrados

============================================================
📊 RESUMO DA ANÁLISE
============================================================

📁 Arquivos analisados: 15
📝 Linhas de código: 2450
📊 Total de issues: 12

  🔴 Críticos: 2
  🟠 Altos: 3
  🟡 Médios: 5
  🟢 Baixos: 2
  ℹ️  Informativos: 0

============================================================
🔴 ISSUES CRÍTICOS
============================================================

1. Credencial AWS detectada
   📄 config/test.py:15
   💡 Remova credenciais hardcoded do código

2. Senha em texto plano
   📄 src/auth.py:42
   💡 Use variáveis de ambiente

🔴 ANÁLISE REPROVADA - Issues críticos encontrados!

============================================================

💾 Relatório salvo em: bob-local-report.json
```

## 🎯 Criando um Projeto de Teste

Vamos criar um projeto simples para testar:

### 1. Crie um diretório de teste

```bash
mkdir ../meu-teste-bob
cd ../meu-teste-bob
```

### 2. Crie um arquivo Python com problemas

```bash
cat > app.py << 'EOF'
# app.py - Exemplo com problemas de segurança

import os

# ❌ PROBLEMA: Credencial hardcoded
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
password = "senha123"

# ❌ PROBLEMA: Função muito longa
def processar_dados(dados):
    resultado = []
    for item in dados:
        if item > 0:
            resultado.append(item * 2)
        else:
            resultado.append(0)
    # ... imagine 100 linhas aqui ...
    return resultado

# ✅ OK: Função simples
def somar(a, b):
    """Soma dois números"""
    return a + b

if __name__ == "__main__":
    print("Teste BOB")
EOF
```

### 3. Execute o BOB

```bash
cd ../bob-pr-orchestrator
python bob_local_test.py ../meu-teste-bob
```

O BOB deve detectar:
- 🔴 Credencial AWS hardcoded
- 🔴 Senha hardcoded
- 🟡 Função sem docstring

## 🔍 Verificando o Relatório JSON

O relatório JSON contém todos os detalhes:

```bash
cat bob-local-report.json | python -m json.tool
```

Estrutura do relatório:

```json
{
  "summary": {
    "total_files": 1,
    "total_lines": 25,
    "total_issues": 3,
    "critical": 2,
    "high": 0,
    "medium": 1,
    "low": 0,
    "info": 0
  },
  "issues": [
    {
      "file_path": "app.py",
      "line_number": 6,
      "severity": "CRITICAL",
      "category": "security",
      "message": "AWS Access Key ID detectada",
      "description": "Credenciais AWS não devem estar no código",
      "suggestion": "Use variáveis de ambiente ou AWS Secrets Manager"
    }
  ],
  "should_block": true
}
```

## 🐛 Troubleshooting

### Erro: ModuleNotFoundError

```bash
# Certifique-se de estar no diretório correto
cd bob-pr-orchestrator

# Reinstale as dependências
pip install -r requirements.txt
```

### Erro: No module named 'bob'

```bash
# Execute a partir do diretório raiz do projeto
python bob_local_test.py .
```

### Nenhum arquivo encontrado

```bash
# Verifique se há arquivos com as extensões corretas
ls -la *.py

# Ou especifique o diretório correto
python bob_local_test.py /caminho/completo/do/projeto
```

## 📚 Próximos Passos

1. ✅ Teste o BOB localmente
2. 📝 Ajuste as políticas em `config/ibm_policies.yaml`
3. 🔧 Configure para GitHub Actions (veja `.github/workflows/bob-pr-check.yml`)
4. 🚀 Integre no seu projeto

## 💡 Dicas

- Use `--extensions .py` para analisar apenas Python
- O BOB ignora automaticamente `venv/`, `node_modules/`, `.git/`
- Issues críticos fazem o comando retornar código de saída 1
- O relatório JSON pode ser usado em pipelines CI/CD

## 🎓 Exemplos de Uso

### Analisar apenas arquivos modificados (Git)

```bash
# Lista arquivos modificados
git diff --name-only HEAD | grep '\.py$' > files.txt

# Analisa cada arquivo
while read file; do
    python bob_local_test.py "$(dirname "$file")" --extensions .py
done < files.txt
```

### Integrar com pre-commit hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
python bob_local_test.py . --extensions .py
if [ $? -ne 0 ]; then
    echo "❌ BOB encontrou issues críticos. Commit bloqueado."
    exit 1
fi
```

## 📞 Suporte

Se encontrar problemas:

1. Verifique se todas as dependências estão instaladas
2. Confirme que está usando Python 3.11+
3. Veja os logs de erro completos
4. Abra uma issue no repositório

---

**Desenvolvido com ❤️ pela equipe IBM Development**

*"Automatizando qualidade, um PR por vez"* 🚀