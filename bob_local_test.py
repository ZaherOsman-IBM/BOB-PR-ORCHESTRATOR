#!/usr/bin/env python3
"""
BOB Local Test - Versão simplificada para testar análise de código localmente
Não requer GitLab/GitHub, apenas analisa arquivos do diretório
"""

import sys
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any

# Importa componentes do BOB
from bob.analyzers.analyzer_factory import AnalyzerFactory
from bob.analyzers.base_analyzer import Issue, Severity
from bob.compliance.security_checker import SecurityChecker


class BOBLocalAnalyzer:
    """Analisador local do BOB para testes"""
    
    def __init__(self, config_path: str = "config/ibm_policies.yaml"):
        """Inicializa o analisador local"""
        self.config = self._load_config(config_path)
        self.security_checker = SecurityChecker(self.config)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carrega arquivo de configuração YAML"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️  Aviso: Não foi possível carregar {config_path}: {e}")
            print("📝 Usando configuração padrão\n")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão"""
        return {
            'security': {
                'block_on_credentials': True,
                'scan_for_secrets': True
            },
            'architecture': {
                'python': {
                    'max_function_lines': 50,
                    'require_docstrings': True
                }
            }
        }
    
    def analyze_directory(self, directory: str, extensions: List[str] = None) -> Dict[str, Any]:
        """
        Analisa todos os arquivos em um diretório
        
        Args:
            directory: Caminho do diretório
            extensions: Lista de extensões para analisar (ex: ['.py', '.js'])
        """
        if extensions is None:
            extensions = ['.py', '.js', '.java', '.swift', '.ts', '.tsx']
        
        print(f"\n{'='*60}")
        print(f"🤖 BOB - Análise Local de Código")
        print(f"{'='*60}\n")
        print(f"📁 Diretório: {directory}")
        print(f"🔍 Extensões: {', '.join(extensions)}\n")
        
        # Encontra arquivos
        path = Path(directory)
        files_to_analyze = []
        
        for ext in extensions:
            files_to_analyze.extend(path.rglob(f"*{ext}"))
        
        # Remove arquivos em diretórios ignorados
        ignored_dirs = {'venv', 'node_modules', '.git', '__pycache__', 'dist', 'build'}
        files_to_analyze = [
            f for f in files_to_analyze 
            if not any(ignored in f.parts for ignored in ignored_dirs)
        ]
        
        print(f"📊 Arquivos encontrados: {len(files_to_analyze)}\n")
        
        if not files_to_analyze:
            print("⚠️  Nenhum arquivo encontrado para análise!")
            return self._empty_result()
        
        # Analisa cada arquivo
        all_issues = []
        analyzed_files = 0
        total_lines = 0
        
        for file_path in files_to_analyze:
            print(f"  🔍 Analisando: {file_path.relative_to(path)}")
            
            try:
                # Cria analisador apropriado
                analyzer = AnalyzerFactory.create_analyzer(str(file_path), self.config)
                
                if analyzer:
                    # Análise de código
                    result = analyzer.analyze_file(str(file_path))
                    all_issues.extend(result.issues)
                    analyzed_files += 1
                    total_lines += result.total_lines
                    
                    # Verificação de segurança
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    security_issues = self.security_checker.check_file(
                        str(file_path),
                        content
                    )
                    all_issues.extend(security_issues)
                    
                    issue_count = len(result.issues) + len(security_issues)
                    if issue_count > 0:
                        print(f"    ⚠️  {issue_count} issues encontrados")
                    else:
                        print(f"    ✅ Sem issues")
                else:
                    print(f"    ⊘ Sem analisador disponível")
                    
            except Exception as e:
                print(f"    ❌ Erro: {str(e)}")
        
        # Gera resumo
        print(f"\n{'='*60}")
        print("📊 RESUMO DA ANÁLISE")
        print(f"{'='*60}\n")
        
        summary = self._generate_summary(analyzed_files, total_lines, all_issues)
        self._print_summary(summary)
        
        # Mostra issues críticos
        critical_issues = [i for i in all_issues if i.severity == Severity.CRITICAL]
        if critical_issues:
            print(f"\n{'='*60}")
            print("🔴 ISSUES CRÍTICOS")
            print(f"{'='*60}\n")
            
            for idx, issue in enumerate(critical_issues[:10], 1):
                print(f"{idx}. {issue.message}")
                print(f"   📄 {issue.file_path}:{issue.line_number}")
                if issue.description:
                    print(f"   💡 {issue.description}")
                print()
            
            if len(critical_issues) > 10:
                print(f"... e mais {len(critical_issues) - 10} issues críticos\n")
        
        # Resultado final
        should_block = len(critical_issues) > 0
        
        if should_block:
            print("\n🔴 ANÁLISE REPROVADA - Issues críticos encontrados!")
        else:
            print("\n✅ ANÁLISE APROVADA - Nenhum issue crítico!")
        
        result = {
            'summary': summary,
            'issues': [self._issue_to_dict(i) for i in all_issues],
            'should_block': should_block
        }
        
        print(f"\n{'='*60}\n")
        
        return result
    
    def _generate_summary(self, files: int, lines: int, issues: List[Issue]) -> Dict[str, Any]:
        """Gera resumo da análise"""
        return {
            'total_files': files,
            'total_lines': lines,
            'total_issues': len(issues),
            'critical': len([i for i in issues if i.severity == Severity.CRITICAL]),
            'high': len([i for i in issues if i.severity == Severity.HIGH]),
            'medium': len([i for i in issues if i.severity == Severity.MEDIUM]),
            'low': len([i for i in issues if i.severity == Severity.LOW]),
            'info': len([i for i in issues if i.severity == Severity.INFO]),
        }
    
    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """Imprime resumo formatado"""
        print(f"📁 Arquivos analisados: {summary['total_files']}")
        print(f"📝 Linhas de código: {summary['total_lines']}")
        print(f"📊 Total de issues: {summary['total_issues']}")
        print(f"\n  🔴 Críticos: {summary['critical']}")
        print(f"  🟠 Altos: {summary['high']}")
        print(f"  🟡 Médios: {summary['medium']}")
        print(f"  🟢 Baixos: {summary['low']}")
        print(f"  ℹ️  Informativos: {summary['info']}")
    
    def _issue_to_dict(self, issue: Issue) -> Dict[str, Any]:
        """Converte Issue para dicionário"""
        return {
            'file_path': issue.file_path,
            'line_number': issue.line_number,
            'severity': issue.severity.value,
            'category': issue.category.value,
            'message': issue.message,
            'description': issue.description,
            'suggestion': issue.suggestion
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """Retorna resultado vazio"""
        return {
            'summary': {
                'total_files': 0,
                'total_lines': 0,
                'total_issues': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            },
            'issues': [],
            'should_block': False
        }
    
    def save_report(self, result: Dict[str, Any], output_path: str) -> None:
        """Salva relatório em arquivo JSON"""
        try:
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"💾 Relatório salvo em: {output_path}")
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='BOB Local Test - Análise de código sem GitLab/GitHub'
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Diretório para analisar (padrão: diretório atual)'
    )
    
    parser.add_argument(
        '--extensions',
        nargs='+',
        help='Extensões de arquivo para analisar (ex: .py .js)'
    )
    
    parser.add_argument(
        '--output',
        default='bob-local-report.json',
        help='Arquivo de saída para o relatório'
    )
    
    parser.add_argument(
        '--config',
        default='config/ibm_policies.yaml',
        help='Arquivo de configuração'
    )
    
    args = parser.parse_args()
    
    try:
        # Inicializa analisador
        analyzer = BOBLocalAnalyzer(config_path=args.config)
        
        # Analisa diretório
        result = analyzer.analyze_directory(
            args.directory,
            extensions=args.extensions
        )
        
        # Salva relatório
        analyzer.save_report(result, args.output)
        
        # Retorna código de saída
        if result['should_block']:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()

# Made with Bob
