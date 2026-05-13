#!/usr/bin/env python3
"""
Script de teste local para BOB
Testa os analisadores sem precisar de GitLab
"""

import sys
import os
import yaml
import json
from pathlib import Path

# Adiciona o diretório bob ao path
sys.path.insert(0, str(Path(__file__).parent))

from bob.analyzers.analyzer_factory import AnalyzerFactory
from bob.compliance.security_checker import SecurityChecker
from bob.analyzers.base_analyzer import Severity


def load_config(config_path: str) -> dict:
    """Carrega arquivo de configuração"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def print_header(text: str):
    """Imprime cabeçalho formatado"""
    print(f"\n{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}\n")


def print_issue(issue, index: int):
    """Imprime um issue formatado"""
    severity_emoji = {
        'CRITICAL': '🔴',
        'HIGH': '🟠',
        'MEDIUM': '🟡',
        'LOW': '🟢',
        'INFO': 'ℹ️'
    }
    
    emoji = severity_emoji.get(issue.severity.value, '❓')
    print(f"{index}. {emoji} [{issue.severity.value}] {issue.message}")
    print(f"   📁 {issue.file_path}:{issue.line_number}")
    if issue.description:
        print(f"   📝 {issue.description}")
    if issue.suggestion:
        print(f"   💡 {issue.suggestion}")
    print()


def test_file(file_path: str, config: dict):
    """Testa análise de um arquivo"""
    print(f"🔍 Analisando: {file_path}")
    
    # Cria analisador
    analyzer = AnalyzerFactory.create_analyzer(file_path, config)
    
    if not analyzer:
        print(f"   ⊘ Sem analisador disponível para este tipo de arquivo\n")
        return None
    
    print(f"   ✓ Usando: {analyzer.name}")
    
    # Analisa arquivo
    result = analyzer.analyze_file(file_path)
    
    # Verifica segurança
    security_checker = SecurityChecker(config)
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        security_issues = security_checker.check_file(file_path, content)
        result.issues.extend(security_issues)
    except Exception as e:
        print(f"   ⚠️  Erro na verificação de segurança: {e}")
    
    # Estatísticas
    print(f"   📊 {len(result.issues)} issues encontrados")
    print(f"   📝 {result.total_lines} linhas analisadas\n")
    
    return result


def print_summary(results: list):
    """Imprime resumo consolidado"""
    print_header("📊 RESUMO CONSOLIDADO")
    
    all_issues = []
    total_files = 0
    total_lines = 0
    
    for result in results:
        if result:
            all_issues.extend(result.issues)
            total_files += result.total_files
            total_lines += result.total_lines
    
    # Conta por severidade
    critical = len([i for i in all_issues if i.severity == Severity.CRITICAL])
    high = len([i for i in all_issues if i.severity == Severity.HIGH])
    medium = len([i for i in all_issues if i.severity == Severity.MEDIUM])
    low = len([i for i in all_issues if i.severity == Severity.LOW])
    info = len([i for i in all_issues if i.severity == Severity.INFO])
    
    print(f"📁 Arquivos analisados: {total_files}")
    print(f"📝 Linhas de código: {total_lines}")
    print(f"📊 Total de issues: {len(all_issues)}")
    print(f"\n  🔴 Críticos: {critical}")
    print(f"  🟠 Altos: {high}")
    print(f"  🟡 Médios: {medium}")
    print(f"  🟢 Baixos: {low}")
    print(f"  ℹ️  Informativos: {info}")
    
    # Issues críticos
    if critical > 0:
        print(f"\n{'='*60}")
        print("🔴 ISSUES CRÍTICOS (Bloqueariam PR)")
        print(f"{'='*60}\n")
        
        critical_issues = [i for i in all_issues if i.severity == Severity.CRITICAL]
        for idx, issue in enumerate(critical_issues, 1):
            print_issue(issue, idx)
    
    # Decisão
    print(f"\n{'='*60}")
    if critical > 0:
        print("❌ PR SERIA BLOQUEADO - Erros críticos encontrados!")
    else:
        print("✅ PR SERIA APROVADO - Pode prosseguir para revisão humana")
    print(f"{'='*60}\n")
    
    return all_issues


def main():
    """Função principal"""
    print_header("🤖 BOB - Teste Local de Análise")
    
    # Carrega configuração
    config_path = "config/ibm_policies.yaml"
    print(f"📋 Carregando configuração: {config_path}")
    
    try:
        config = load_config(config_path)
        print("✓ Configuração carregada com sucesso\n")
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return 1
    
    # Arquivos de teste
    test_files = [
        "test_samples/test_python.py",
        "test_samples/test_java.java",
        "test_samples/test_react.tsx",
    ]
    
    print_header("🔍 ANÁLISE DE ARQUIVOS")
    
    results = []
    for file_path in test_files:
        if os.path.exists(file_path):
            result = test_file(file_path, config)
            results.append(result)
        else:
            print(f"⚠️  Arquivo não encontrado: {file_path}\n")
    
    # Resumo
    all_issues = print_summary(results)
    
    # Salva relatório
    report_path = "bob-test-report.json"
    try:
        report = {
            'total_files': len([r for r in results if r]),
            'total_issues': len(all_issues),
            'issues': [i.to_dict() for i in all_issues]
        }
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"💾 Relatório salvo em: {report_path}")
    except Exception as e:
        print(f"⚠️  Erro ao salvar relatório: {e}")
    
    # Retorna código de saída
    critical_count = len([i for i in all_issues if i.severity == Severity.CRITICAL])
    return 1 if critical_count > 0 else 0


if __name__ == '__main__':
    sys.exit(main())

# Made with Bob
