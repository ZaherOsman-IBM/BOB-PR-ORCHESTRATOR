"""
Swift Code Analyzer
Analisador de código Swift com foco em arquitetura VIPER
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


class SwiftAnalyzer(BaseAnalyzer):
    """Analisador específico para código Swift"""
    
    # Extensões de arquivo Swift
    SWIFT_EXTENSIONS = {'.swift'}
    
    # Padrões VIPER
    VIPER_COMPONENTS = ['View', 'Interactor', 'Presenter', 'Entity', 'Router']
    
    def _get_language(self) -> str:
        return "Swift"
    
    def can_analyze(self, file_path: str) -> bool:
        """Verifica se o arquivo é Swift"""
        return self._get_file_extension(file_path) in self.SWIFT_EXTENSIONS
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analisa um arquivo Swift"""
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
            self._check_viper_architecture(file_path, content, result)
            self._check_function_length(file_path, content, result)
            self._check_class_length(file_path, content, result)
            self._check_naming_conventions(file_path, content, result)
            self._check_memory_leaks(file_path, content, result)
            self._check_force_unwrapping(file_path, content, result)
            self._check_protocols(file_path, content, result)
            
        except Exception as e:
            result.success = False
            result.error_message = f"Erro ao analisar {file_path}: {str(e)}"
        
        return result
    
    def _check_viper_architecture(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica conformidade com arquitetura VIPER"""
        if not self.config.get('architecture', {}).get('swift', {}).get('enforce_viper', False):
            return
        
        file_name = Path(file_path).stem
        
        # Verifica se é um componente VIPER
        is_viper_component = any(comp in file_name for comp in self.VIPER_COMPONENTS)
        
        if is_viper_component:
            # ViewController não deve ter lógica de negócio
            if 'ViewController' in file_name or 'View' in file_name:
                # Procura por lógica de negócio no View
                business_logic_patterns = [
                    r'func\s+\w+\([^)]*\)\s*{[^}]*(?:URLSession|Alamofire|fetch|save|delete)',
                    r'let\s+\w+\s*=\s*(?:URLSession|Alamofire)',
                ]
                
                for pattern in business_logic_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        result.add_issue(self._create_issue(
                            file_path=file_path,
                            line_number=line_num,
                            message="Lógica de negócio detectada no View Controller",
                            description="Em VIPER, a lógica de negócio deve estar no Interactor, não no View",
                            severity=Severity.HIGH,
                            category=IssueCategory.ARCHITECTURE,
                            rule_id="VIPER001",
                            rule_name="No Business Logic in View",
                            suggestion="Mova esta lógica para o Interactor correspondente"
                        ))
            
            # Presenter não deve acessar UIKit diretamente
            if 'Presenter' in file_name:
                uikit_pattern = r'import\s+UIKit|UI[A-Z]\w+'
                matches = re.finditer(uikit_pattern, content)
                for match in matches:
                    if 'import UIKit' not in match.group():  # Ignora import
                        line_num = content[:match.start()].count('\n') + 1
                        result.add_issue(self._create_issue(
                            file_path=file_path,
                            line_number=line_num,
                            message="Presenter não deve acessar UIKit diretamente",
                            description="Use protocolos para comunicação com a View",
                            severity=Severity.MEDIUM,
                            category=IssueCategory.ARCHITECTURE,
                            rule_id="VIPER002",
                            rule_name="No UIKit in Presenter"
                        ))
    
    def _check_function_length(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica tamanho das funções"""
        max_lines = self.config.get('architecture', {}).get('swift', {}).get('max_function_lines', 50)
        
        # Encontra todas as funções
        func_pattern = r'func\s+(\w+)\s*\([^)]*\)\s*(?:->\s*\w+\s*)?{'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            match = re.search(func_pattern, line)
            if match:
                func_name = match.group(1)
                # Conta linhas até o fechamento da função
                brace_count = 1
                func_lines = 1
                j = i + 1
                
                while j < len(lines) and brace_count > 0:
                    func_lines += 1
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    j += 1
                
                if func_lines > max_lines:
                    result.add_issue(self._create_issue(
                        file_path=file_path,
                        line_number=i + 1,
                        message=f"Função '{func_name}' muito longa ({func_lines} linhas)",
                        description=f"Funções devem ter no máximo {max_lines} linhas",
                        severity=Severity.MEDIUM,
                        category=IssueCategory.CODE_QUALITY,
                        rule_id="SWIFT001",
                        rule_name="Function Too Long",
                        suggestion="Considere dividir esta função em funções menores"
                    ))
    
    def _check_class_length(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica tamanho das classes"""
        max_lines = self.config.get('architecture', {}).get('swift', {}).get('max_class_lines', 350)
        
        # Encontra classes
        class_pattern = r'class\s+(\w+)'
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
                        rule_id="SWIFT002",
                        rule_name="Class Too Long",
                        suggestion="Considere dividir esta classe em classes menores"
                    ))
    
    def _check_naming_conventions(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica convenções de nomenclatura Swift"""
        lines = content.split('\n')
        
        # Classes devem ser PascalCase
        class_pattern = r'class\s+([a-z]\w*)'
        for i, line in enumerate(lines):
            match = re.search(class_pattern, line)
            if match:
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=i + 1,
                    message=f"Nome de classe '{match.group(1)}' deve começar com letra maiúscula",
                    severity=Severity.LOW,
                    category=IssueCategory.STYLE,
                    rule_id="SWIFT003",
                    rule_name="Class Naming Convention"
                ))
        
        # Variáveis devem ser camelCase
        var_pattern = r'(?:var|let)\s+([A-Z]\w*)\s*[:=]'
        for i, line in enumerate(lines):
            match = re.search(var_pattern, line)
            if match and not match.group(1).isupper():  # Ignora constantes
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=i + 1,
                    message=f"Nome de variável '{match.group(1)}' deve começar com letra minúscula",
                    severity=Severity.LOW,
                    category=IssueCategory.STYLE,
                    rule_id="SWIFT004",
                    rule_name="Variable Naming Convention"
                ))
    
    def _check_memory_leaks(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica possíveis memory leaks (retain cycles)"""
        # Procura por closures sem [weak self] ou [unowned self]
        closure_pattern = r'{\s*(?!\[(?:weak|unowned)\s+self\])[^}]*self\.'
        
        matches = re.finditer(closure_pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            result.add_issue(self._create_issue(
                file_path=file_path,
                line_number=line_num,
                message="Possível retain cycle detectado",
                description="Closure captura 'self' sem [weak self] ou [unowned self]",
                severity=Severity.HIGH,
                category=IssueCategory.CODE_QUALITY,
                rule_id="SWIFT005",
                rule_name="Potential Retain Cycle",
                suggestion="Use [weak self] ou [unowned self] na captura da closure"
            ))
    
    def _check_force_unwrapping(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica uso de force unwrapping (!)"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Ignora comentários
            if '//' in line:
                line = line[:line.index('//')]
            
            # Procura por ! (exceto em declarações de tipo)
            if '!' in line and not re.search(r':\s*\w+!', line):
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=i + 1,
                    message="Force unwrapping detectado",
                    description="Evite usar ! para unwrap optionals",
                    severity=Severity.MEDIUM,
                    category=IssueCategory.CODE_QUALITY,
                    rule_id="SWIFT006",
                    rule_name="Avoid Force Unwrapping",
                    suggestion="Use if let, guard let, ou optional chaining (?) ao invés de !"
                ))
    
    def _check_protocols(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica uso adequado de protocolos"""
        if not self.config.get('architecture', {}).get('swift', {}).get('require_protocols', False):
            return
        
        # Verifica se componentes VIPER têm protocolos
        file_name = Path(file_path).stem
        
        if any(comp in file_name for comp in ['Presenter', 'Interactor', 'Router']):
            if 'protocol' not in content.lower():
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=1,
                    message=f"Componente VIPER '{file_name}' deve definir um protocolo",
                    description="Componentes VIPER devem usar protocolos para desacoplamento",
                    severity=Severity.MEDIUM,
                    category=IssueCategory.ARCHITECTURE,
                    rule_id="VIPER003",
                    rule_name="VIPER Component Protocol Required",
                    suggestion="Defina um protocolo para este componente"
                ))

# Made with Bob
