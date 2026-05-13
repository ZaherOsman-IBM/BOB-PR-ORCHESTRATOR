"""
Python Code Analyzer
Analisador de código Python com verificações PEP 8 e boas práticas
"""

import re
import ast
from typing import List, Dict, Any
from pathlib import Path

from .base_analyzer import (
    BaseAnalyzer,
    AnalysisResult,
    Issue,
    Severity,
    IssueCategory
)


class PythonAnalyzer(BaseAnalyzer):
    """Analisador específico para código Python"""
    
    # Extensões de arquivo Python
    PYTHON_EXTENSIONS = {'.py', '.pyw'}
    
    def _get_language(self) -> str:
        return "Python"
    
    def can_analyze(self, file_path: str) -> bool:
        """Verifica se o arquivo é Python"""
        return self._get_file_extension(file_path) in self.PYTHON_EXTENSIONS
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analisa um arquivo Python"""
        result = AnalysisResult(
            analyzer_name=self.name,
            language=self.language,
            files_analyzed=[file_path]
        )
        
        try:
            content = self._read_file(file_path)
            result.total_lines = self._count_lines(file_path)
            result.total_files = 1
            
            # Executar verificações
            self._check_syntax(file_path, content, result)
            self._check_function_length(file_path, content, result)
            self._check_class_length(file_path, content, result)
            self._check_docstrings(file_path, content, result)
            self._check_type_hints(file_path, content, result)
            self._check_imports(file_path, content, result)
            self._check_naming_conventions(file_path, content, result)
            self._check_complexity(file_path, content, result)
            
        except Exception as e:
            result.success = False
            result.error_message = f"Erro ao analisar {file_path}: {str(e)}"
        
        return result
    
    def _check_syntax(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica erros de sintaxe"""
        try:
            ast.parse(content)
        except SyntaxError as e:
            result.add_issue(self._create_issue(
                file_path=file_path,
                line_number=e.lineno or 1,
                column=e.offset,
                message=f"Erro de sintaxe: {e.msg}",
                severity=Severity.CRITICAL,
                category=IssueCategory.CODE_QUALITY,
                rule_id="PY001",
                rule_name="Syntax Error"
            ))
    
    def _check_function_length(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica tamanho das funções"""
        max_lines = self.config.get('architecture', {}).get('python', {}).get('max_function_lines', 30)
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno + 1
                    if func_lines > max_lines:
                        result.add_issue(self._create_issue(
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Função '{node.name}' muito longa ({func_lines} linhas)",
                            description=f"Funções devem ter no máximo {max_lines} linhas",
                            severity=Severity.MEDIUM,
                            category=IssueCategory.CODE_QUALITY,
                            rule_id="PY002",
                            rule_name="Function Too Long",
                            suggestion="Considere dividir esta função em funções menores"
                        ))
        except:
            pass
    
    def _check_class_length(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica tamanho das classes"""
        max_lines = self.config.get('architecture', {}).get('python', {}).get('max_class_lines', 300)
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_lines = node.end_lineno - node.lineno + 1
                    if class_lines > max_lines:
                        result.add_issue(self._create_issue(
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Classe '{node.name}' muito longa ({class_lines} linhas)",
                            description=f"Classes devem ter no máximo {max_lines} linhas",
                            severity=Severity.MEDIUM,
                            category=IssueCategory.CODE_QUALITY,
                            rule_id="PY003",
                            rule_name="Class Too Long"
                        ))
        except:
            pass
    
    def _check_docstrings(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica presença de docstrings"""
        if not self.config.get('architecture', {}).get('python', {}).get('require_docstrings', False):
            return
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    # Ignora funções privadas e métodos especiais
                    if node.name.startswith('_') and not node.name.startswith('__'):
                        continue
                    
                    # Verifica se tem docstring
                    has_docstring = (
                        ast.get_docstring(node) is not None
                    )
                    
                    if not has_docstring:
                        node_type = "Função" if isinstance(node, ast.FunctionDef) else "Classe"
                        result.add_issue(self._create_issue(
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"{node_type} '{node.name}' sem docstring",
                            description="Funções e classes públicas devem ter docstrings",
                            severity=Severity.LOW,
                            category=IssueCategory.DOCUMENTATION,
                            rule_id="PY004",
                            rule_name="Missing Docstring",
                            suggestion="Adicione uma docstring explicando o propósito e parâmetros"
                        ))
        except:
            pass
    
    def _check_type_hints(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica presença de type hints"""
        if not self.config.get('architecture', {}).get('python', {}).get('require_type_hints', False):
            return
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Ignora funções privadas e métodos especiais
                    if node.name.startswith('_'):
                        continue
                    
                    # Verifica type hints nos parâmetros
                    for arg in node.args.args:
                        if arg.annotation is None and arg.arg != 'self' and arg.arg != 'cls':
                            result.add_issue(self._create_issue(
                                file_path=file_path,
                                line_number=node.lineno,
                                message=f"Parâmetro '{arg.arg}' sem type hint",
                                severity=Severity.LOW,
                                category=IssueCategory.CODE_QUALITY,
                                rule_id="PY005",
                                rule_name="Missing Type Hint"
                            ))
                    
                    # Verifica type hint no retorno
                    if node.returns is None and node.name != '__init__':
                        result.add_issue(self._create_issue(
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Função '{node.name}' sem type hint de retorno",
                            severity=Severity.LOW,
                            category=IssueCategory.CODE_QUALITY,
                            rule_id="PY006",
                            rule_name="Missing Return Type Hint"
                        ))
        except:
            pass
    
    def _check_imports(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica organização dos imports"""
        lines = content.split('\n')
        
        import_section_ended = False
        last_import_line = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Ignora linhas vazias e comentários
            if not stripped or stripped.startswith('#'):
                continue
            
            is_import = stripped.startswith('import ') or stripped.startswith('from ')
            
            if is_import:
                last_import_line = i
                if import_section_ended:
                    result.add_issue(self._create_issue(
                        file_path=file_path,
                        line_number=i + 1,
                        message="Import fora da seção de imports",
                        description="Todos os imports devem estar no início do arquivo",
                        severity=Severity.LOW,
                        category=IssueCategory.STYLE,
                        rule_id="PY007",
                        rule_name="Import Organization"
                    ))
            elif not is_import and stripped and last_import_line > 0:
                import_section_ended = True
    
    def _check_naming_conventions(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica convenções de nomenclatura PEP 8"""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Classes devem ser PascalCase
                if isinstance(node, ast.ClassDef):
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                        result.add_issue(self._create_issue(
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Nome de classe '{node.name}' deve ser PascalCase",
                            severity=Severity.LOW,
                            category=IssueCategory.STYLE,
                            rule_id="PY008",
                            rule_name="Class Naming Convention"
                        ))
                
                # Funções devem ser snake_case
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('__'):  # Ignora métodos especiais
                        if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                            result.add_issue(self._create_issue(
                                file_path=file_path,
                                line_number=node.lineno,
                                message=f"Nome de função '{node.name}' deve ser snake_case",
                                severity=Severity.LOW,
                                category=IssueCategory.STYLE,
                                rule_id="PY009",
                                rule_name="Function Naming Convention"
                            ))
        except:
            pass
    
    def _check_complexity(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica complexidade ciclomática"""
        max_complexity = self.config.get('code_quality', {}).get('max_complexity', 10)
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > max_complexity:
                        result.add_issue(self._create_issue(
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Função '{node.name}' muito complexa (complexidade: {complexity})",
                            description=f"Complexidade ciclomática deve ser no máximo {max_complexity}",
                            severity=Severity.MEDIUM,
                            category=IssueCategory.CODE_QUALITY,
                            rule_id="PY010",
                            rule_name="High Complexity",
                            suggestion="Simplifique a lógica ou divida em funções menores"
                        ))
        except:
            pass
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calcula complexidade ciclomática de uma função"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

# Made with Bob
