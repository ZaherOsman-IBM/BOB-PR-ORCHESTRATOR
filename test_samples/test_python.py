"""
Arquivo de teste Python com vários problemas propositais
para testar o BOB Analyzer
"""

# ❌ Senha hardcoded (CRÍTICO)
password = "minha-senha-123"
api_key = "AKIAIOSFODNN7EXAMPLE"

# ❌ Função muito longa (> 30 linhas)
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
        else:
            result.append(0)
    
    # Mais 20 linhas de código...
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    
    return result

# ❌ Classe com nome errado (deve ser PascalCase)
class myClass:
    pass

# ❌ Função sem docstring
def calculate_total(items):
    return sum(items)

# ❌ Função sem type hints
def get_user(user_id):
    return {"id": user_id, "name": "Test"}

# ✅ Função correta
def process_items(items: list) -> list:
    """
    Processa lista de items.
    
    Args:
        items: Lista de items para processar
        
    Returns:
        Lista processada
    """
    return [item * 2 for item in items]

# Made with Bob
