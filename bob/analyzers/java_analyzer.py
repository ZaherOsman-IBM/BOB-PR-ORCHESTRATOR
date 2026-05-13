"""
Java Code Analyzer
Analisador de código Java com verificações de padrões e boas práticas
"""

import re
from typing import List, Dict, Any
from pathlib import Path

from .base_analyzer import (
    BaseAnalyzer,
    AnalysisResult,
    Issue,
    Severity,
    IssueCategory
)


class JavaAnalyzer(BaseAnalyzer):
    """Analisador específico para código Java"""
    
    # Extensões de arquivo Java
    JAVA_EXTENSIONS = {'.java'}
    
    def _get_language(self) -> str:
        return "Java"
    
    def can_analyze(self, file_path: str) -> bool:
        """Verifica se o arquivo é Java"""
        return self._get_file_extension(file_path) in self.JAVA_EXTENSIONS
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analisa um arquivo Java"""
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
            self._check_class_length(file_path, content, result)
            self._check_method_length(file_path, content, result)
            self._check_exception_handling(file_path, content, result)
            self._check_naming_conventions(file_path, content, result)
            self._check_design_patterns(file_path, content, result)
            self._check_null_checks(file_path, content, result)
            self._check_stream_usage(file_path, content, result)
            self._check_deprecated_apis(file_path, content, result)
            
        except Exception as e:
            result.success = False
            result.error_message = f"Erro ao analisar {file_path}: {str(e)}"
        
        return result
    
    def _check_class_length(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica tamanho das classes"""
        max_lines = self.config.get('architecture', {}).get('java', {}).get('max_class_lines', 500)
        
        # Encontra classes
        class_pattern = r'(?:public|private|protected)?\s*(?:static|final|abstract)?\s*class\s+(\w+)'
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            match = re.search(class_pattern, line)
            if match:
                class_name = match.group(1)
                # Conta linhas da classe
                brace_count = 0
                class_lines = 0
                j = i
                
                while j < len(lines):
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    class_lines += 1
                    if brace_count == 0 and '{' in lines[i]:
                        break
                    j += 1
                
                if class_lines > max_lines:
                    result.add_issue(self._create_issue(
                        file_path=file_path,
                        line_number=i + 1,
                        message=f"Classe '{class_name}' muito longa ({class_lines} linhas)",
                        description=f"Classes devem ter no máximo {max_lines} linhas",
                        severity=Severity.MEDIUM,
                        category=IssueCategory.CODE_QUALITY,
                        rule_id="JAVA001",
                        rule_name="Class Too Long",
                        suggestion="Considere dividir em classes menores ou usar composição"
                    ))
    
    def _check_method_length(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica tamanho dos métodos"""
        max_lines = self.config.get('architecture', {}).get('java', {}).get('max_method_lines', 30)
        
        # Padrão para métodos
        method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+(?:,\s*\w+)*)?\s*{'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            match = re.search(method_pattern, line)
            if match:
                method_name = match.group(1)
                # Ignora construtores e getters/setters simples
                if method_name in ['get', 'set', 'is']:
                    continue
                
                # Conta linhas do método
                brace_count = 1
                method_lines = 1
                j = i + 1
                
                while j < len(lines) and brace_count > 0:
                    method_lines += 1
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    j += 1
                
                if method_lines > max_lines:
                    result.add_issue(self._create_issue(
                        file_path=file_path,
                        line_number=i + 1,
                        message=f"Método '{method_name}' muito longo ({method_lines} linhas)",
                        description=f"Métodos devem ter no máximo {max_lines} linhas",
                        severity=Severity.MEDIUM,
                        category=IssueCategory.CODE_QUALITY,
                        rule_id="JAVA002",
                        rule_name="Method Too Long",
                        suggestion="Extraia lógica para métodos auxiliares privados"
                    ))
    
    def _check_exception_handling(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica tratamento de exceções"""
        lines = content.split('\n')
        
        # Catch genérico (Exception)
        for i, line in enumerate(lines):
            if re.search(r'catch\s*\(\s*Exception\s+\w+\s*\)', line):
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=i + 1,
                    message="Catch genérico de Exception detectado",
                    description="Evite capturar Exception genérica",
                    severity=Severity.MEDIUM,
                    category=IssueCategory.CODE_QUALITY,
                    rule_id="JAVA003",
                    rule_name="Generic Exception Catch",
                    suggestion="Capture exceções específicas (IOException, SQLException, etc.)"
                ))
            
            # Catch vazio
            if 'catch' in line:
                # Verifica se o bloco catch está vazio
                j = i + 1
                while j < len(lines) and '{' not in lines[i]:
                    j += 1
                if j < len(lines) - 1:
                    next_line = lines[j + 1].strip()
                    if next_line == '}' or (j + 2 < len(lines) and lines[j + 2].strip() == '}'):
                        result.add_issue(self._create_issue(
                            file_path=file_path,
                            line_number=i + 1,
                            message="Bloco catch vazio detectado",
                            severity=Severity.HIGH,
                            category=IssueCategory.CODE_QUALITY,
                            rule_id="JAVA004",
                            rule_name="Empty Catch Block",
                            suggestion="Adicione logging ou tratamento adequado da exceção"
                        ))
    
    def _check_naming_conventions(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica convenções de nomenclatura Java"""
        lines = content.split('\n')
        
        # Classes devem ser PascalCase
        class_pattern = r'class\s+([a-z]\w*)'
        for i, line in enumerate(lines):
            match = re.search(class_pattern, line)
            if match:
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=i + 1,
                    message=f"Nome de classe '{match.group(1)}' deve começar com maiúscula",
                    severity=Severity.LOW,
                    category=IssueCategory.STYLE,
                    rule_id="JAVA005",
                    rule_name="Class Naming Convention"
                ))
        
        # Constantes devem ser UPPER_SNAKE_CASE
        const_pattern = r'(?:public|private|protected)\s+static\s+final\s+\w+\s+([a-z]\w*)\s*='
        for i, line in enumerate(lines):
            match = re.search(const_pattern, line)
            if match and not match.group(1).isupper():
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=i + 1,
                    message=f"Constante '{match.group(1)}' deve ser UPPER_SNAKE_CASE",
                    severity=Severity.LOW,
                    category=IssueCategory.STYLE,
                    rule_id="JAVA006",
                    rule_name="Constant Naming Convention"
                ))
    
    def _check_design_patterns(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica uso adequado de design patterns"""
        # Singleton mal implementado
        if 'private static' in content and 'getInstance' in content:
            if 'synchronized' not in content and 'volatile' not in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'getInstance' in line:
                        result.add_issue(self._create_issue(
                            file_path=file_path,
                            line_number=i + 1,
                            message="Singleton possivelmente não thread-safe",
                            description="Singleton sem sincronização adequada",
                            severity=Severity.MEDIUM,
                            category=IssueCategory.ARCHITECTURE,
                            rule_id="JAVA007",
                            rule_name="Unsafe Singleton",
                            suggestion="Use double-checked locking ou enum singleton"
                        ))
                        break
    
    def _check_null_checks(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica tratamento de null"""
        lines = content.split('\n')
        
        # Métodos que retornam null sem @Nullable
        for i, line in enumerate(lines):
            if 'return null' in line:
                # Verifica se tem @Nullable nas linhas anteriores
                has_nullable = False
                for j in range(max(0, i - 5), i):
                    if '@Nullable' in lines[j] or '@CheckForNull' in lines[j]:
                        has_nullable = True
                        break
                
                if not has_nullable:
                    result.add_issue(self._create_issue(
                        file_path=file_path,
                        line_number=i + 1,
                        message="Retorno null sem anotação @Nullable",
                        severity=Severity.LOW,
                        category=IssueCategory.CODE_QUALITY,
                        rule_id="JAVA008",
                        rule_name="Missing Nullable Annotation",
                        suggestion="Adicione @Nullable ou use Optional<T>"
                    ))
    
    def _check_stream_usage(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica uso de Streams modernos"""
        if self.config.get('architecture', {}).get('java', {}).get('enforce_async_await', False):
            # Procura por loops que poderiam ser streams
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if re.search(r'for\s*\([^)]*:\s*\w+\)', line):
                    # Verifica se é um loop simples que poderia ser stream
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if any(op in next_line for op in ['add(', 'put(', 'remove(']):
                            result.add_issue(self._create_issue(
                                file_path=file_path,
                                line_number=i + 1,
                                message="Loop poderia ser substituído por Stream",
                                severity=Severity.LOW,
                                category=IssueCategory.CODE_QUALITY,
                                rule_id="JAVA009",
                                rule_name="Consider Using Streams",
                                suggestion="Use .stream().filter().map().collect() para código mais funcional"
                            ))
    
    def _check_deprecated_apis(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica uso de APIs deprecated"""
        deprecated_apis = [
            ('Date()', 'Use LocalDate, LocalDateTime ou Instant'),
            ('Vector', 'Use ArrayList'),
            ('Hashtable', 'Use HashMap'),
            ('StringBuffer', 'Use StringBuilder (se não precisar de thread-safety)'),
        ]
        
        lines = content.split('\n')
        for api, suggestion in deprecated_apis:
            for i, line in enumerate(lines):
                if api in line and '@SuppressWarnings' not in line:
                    result.add_issue(self._create_issue(
                        file_path=file_path,
                        line_number=i + 1,
                        message=f"API deprecated detectada: {api}",
                        severity=Severity.LOW,
                        category=IssueCategory.CODE_QUALITY,
                        rule_id="JAVA010",
                        rule_name="Deprecated API Usage",
                        suggestion=suggestion
                    ))

# Made with Bob
