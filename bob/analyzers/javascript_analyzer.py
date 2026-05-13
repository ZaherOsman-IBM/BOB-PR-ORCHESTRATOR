"""
JavaScript/TypeScript/React Code Analyzer
Analisador de código JavaScript, TypeScript e React
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


class JavaScriptAnalyzer(BaseAnalyzer):
    """Analisador específico para código JavaScript/TypeScript/React"""
    
    # Extensões de arquivo
    JS_EXTENSIONS = {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}
    
    def _get_language(self) -> str:
        return "JavaScript/TypeScript"
    
    def can_analyze(self, file_path: str) -> bool:
        """Verifica se o arquivo é JavaScript/TypeScript"""
        return self._get_file_extension(file_path) in self.JS_EXTENSIONS
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analisa um arquivo JavaScript/TypeScript"""
        result = AnalysisResult(
            analyzer_name=self.name,
            language=self.language,
            files_analyzed=[file_path]
        )
        
        try:
            content = self._read_file(file_path)
            result.total_lines = self._count_lines(file_path)
            result.total_files = 1
            
            # Determina se é React
            is_react = self._is_react_file(file_path, content)
            is_typescript = file_path.endswith(('.ts', '.tsx'))
            
            # Executar verificações
            self._check_function_length(file_path, content, result)
            self._check_console_log(file_path, content, result)
            self._check_var_usage(file_path, content, result)
            self._check_async_await(file_path, content, result)
            self._check_arrow_functions(file_path, content, result)
            self._check_naming_conventions(file_path, content, result)
            
            if is_react:
                self._check_react_component_length(file_path, content, result)
                self._check_react_hooks(file_path, content, result)
                self._check_react_proptypes(file_path, content, result, is_typescript)
                self._check_react_keys(file_path, content, result)
            
            if is_typescript:
                self._check_typescript_types(file_path, content, result)
            
        except Exception as e:
            result.success = False
            result.error_message = f"Erro ao analisar {file_path}: {str(e)}"
        
        return result
    
    def _is_react_file(self, file_path: str, content: str) -> bool:
        """Verifica se é um arquivo React"""
        return (
            file_path.endswith(('.jsx', '.tsx')) or
            'import React' in content or
            'from \'react\'' in content or
            'from "react"' in content
        )
    
    def _check_function_length(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica tamanho das funções"""
        max_lines = self.config.get('architecture', {}).get('javascript', {}).get('max_function_lines', 25)
        
        # Padrões de função
        function_patterns = [
            r'function\s+(\w+)\s*\([^)]*\)\s*{',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
            r'(\w+)\s*:\s*function\s*\([^)]*\)\s*{',
        ]
        
        lines = content.split('\n')
        for pattern in function_patterns:
            for i, line in enumerate(lines):
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    # Conta linhas da função
                    brace_count = line.count('{') - line.count('}')
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
                            rule_id="JS001",
                            rule_name="Function Too Long",
                            suggestion="Divida em funções menores e mais específicas"
                        ))
    
    def _check_console_log(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica uso de console.log em produção"""
        if not self.config.get('architecture', {}).get('javascript', {}).get('forbid_console_log', True):
            return
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Ignora comentários
            if '//' in line:
                code_part = line[:line.index('//')]
            else:
                code_part = line
            
            if 'console.log' in code_part or 'console.debug' in code_part:
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=i + 1,
                    message="console.log detectado",
                    description="Evite console.log em código de produção",
                    severity=Severity.MEDIUM,
                    category=IssueCategory.CODE_QUALITY,
                    rule_id="JS002",
                    rule_name="Console Log in Production",
                    suggestion="Use um logger apropriado ou remova antes do commit"
                ))
    
    def _check_var_usage(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica uso de var ao invés de let/const"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.search(r'\bvar\s+\w+', line):
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=i + 1,
                    message="Uso de 'var' detectado",
                    description="Use 'const' ou 'let' ao invés de 'var'",
                    severity=Severity.LOW,
                    category=IssueCategory.CODE_QUALITY,
                    rule_id="JS003",
                    rule_name="Avoid Var",
                    suggestion="Prefira 'const' para valores imutáveis, 'let' para mutáveis"
                ))
    
    def _check_async_await(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica uso de async/await vs callbacks"""
        if not self.config.get('architecture', {}).get('javascript', {}).get('enforce_async_await', True):
            return
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Procura por callbacks aninhados (callback hell)
            if line.count('function(') > 1 or line.count('=>') > 1:
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=i + 1,
                    message="Callbacks aninhados detectados",
                    description="Considere usar async/await para melhor legibilidade",
                    severity=Severity.LOW,
                    category=IssueCategory.CODE_QUALITY,
                    rule_id="JS004",
                    rule_name="Prefer Async Await",
                    suggestion="Refatore para usar async/await ou Promises"
                ))
    
    def _check_arrow_functions(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica uso consistente de arrow functions"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Função tradicional onde arrow function seria melhor
            if re.search(r'\.map\s*\(\s*function\s*\(', line):
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=i + 1,
                    message="Use arrow function em callbacks",
                    severity=Severity.LOW,
                    category=IssueCategory.STYLE,
                    rule_id="JS005",
                    rule_name="Prefer Arrow Functions",
                    suggestion="Use arrow function: .map(item => ...)"
                ))
    
    def _check_naming_conventions(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica convenções de nomenclatura"""
        lines = content.split('\n')
        
        # Classes/Componentes devem ser PascalCase
        class_pattern = r'(?:class|function)\s+([a-z]\w*)\s*(?:\(|{|extends)'
        for i, line in enumerate(lines):
            match = re.search(class_pattern, line)
            if match:
                name = match.group(1)
                # Ignora funções utilitárias comuns
                if name not in ['map', 'filter', 'reduce', 'forEach']:
                    result.add_issue(self._create_issue(
                        file_path=file_path,
                        line_number=i + 1,
                        message=f"Componente/Classe '{name}' deve ser PascalCase",
                        severity=Severity.LOW,
                        category=IssueCategory.STYLE,
                        rule_id="JS006",
                        rule_name="Component Naming Convention"
                    ))
    
    def _check_react_component_length(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica tamanho de componentes React"""
        max_lines = self.config.get('architecture', {}).get('javascript', {}).get('max_component_lines', 300)
        
        # Procura por componentes React
        component_patterns = [
            r'(?:function|const)\s+([A-Z]\w+)\s*=?\s*\([^)]*\)\s*(?:=>)?\s*{',
            r'class\s+([A-Z]\w+)\s+extends\s+(?:React\.)?Component',
        ]
        
        lines = content.split('\n')
        for pattern in component_patterns:
            for i, line in enumerate(lines):
                match = re.search(pattern, line)
                if match:
                    component_name = match.group(1)
                    # Conta linhas do componente
                    brace_count = line.count('{') - line.count('}')
                    comp_lines = 1
                    j = i + 1
                    
                    while j < len(lines) and brace_count > 0:
                        comp_lines += 1
                        brace_count += lines[j].count('{') - lines[j].count('}')
                        j += 1
                    
                    if comp_lines > max_lines:
                        result.add_issue(self._create_issue(
                            file_path=file_path,
                            line_number=i + 1,
                            message=f"Componente React '{component_name}' muito longo ({comp_lines} linhas)",
                            description=f"Componentes devem ter no máximo {max_lines} linhas",
                            severity=Severity.MEDIUM,
                            category=IssueCategory.CODE_QUALITY,
                            rule_id="REACT001",
                            rule_name="Component Too Long",
                            suggestion="Divida em componentes menores e mais reutilizáveis"
                        ))
    
    def _check_react_hooks(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica uso correto de React Hooks"""
        lines = content.split('\n')
        
        # Hooks devem começar com 'use'
        hook_pattern = r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{'
        for i, line in enumerate(lines):
            match = re.search(hook_pattern, line)
            if match:
                hook_name = match.group(1)
                # Verifica se usa hooks do React mas não segue convenção
                if any(h in content[i:i+500] for h in ['useState', 'useEffect', 'useContext']):
                    if not hook_name.startswith('use') and hook_name[0].islower():
                        result.add_issue(self._create_issue(
                            file_path=file_path,
                            line_number=i + 1,
                            message=f"Hook customizado '{hook_name}' deve começar com 'use'",
                            severity=Severity.MEDIUM,
                            category=IssueCategory.CODE_QUALITY,
                            rule_id="REACT002",
                            rule_name="Hook Naming Convention",
                            suggestion=f"Renomeie para 'use{hook_name[0].upper()}{hook_name[1:]}'"
                        ))
        
        # useEffect sem array de dependências
        for i, line in enumerate(lines):
            if 'useEffect(' in line:
                # Verifica se tem array de dependências nas próximas linhas
                has_deps = False
                for j in range(i, min(i + 10, len(lines))):
                    if re.search(r'},\s*\[', lines[j]):
                        has_deps = True
                        break
                
                if not has_deps:
                    result.add_issue(self._create_issue(
                        file_path=file_path,
                        line_number=i + 1,
                        message="useEffect sem array de dependências",
                        description="Sempre especifique dependências do useEffect",
                        severity=Severity.HIGH,
                        category=IssueCategory.CODE_QUALITY,
                        rule_id="REACT003",
                        rule_name="Missing Effect Dependencies",
                        suggestion="Adicione array de dependências: useEffect(() => {...}, [deps])"
                    ))
    
    def _check_react_proptypes(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult,
        is_typescript: bool
    ) -> None:
        """Verifica PropTypes ou TypeScript types"""
        if is_typescript:
            return  # TypeScript já tem tipagem
        
        if not self.config.get('architecture', {}).get('javascript', {}).get('require_proptypes', True):
            return
        
        # Procura por componentes sem PropTypes
        component_pattern = r'(?:function|const)\s+([A-Z]\w+)\s*=?\s*\([^)]*\)\s*(?:=>)?\s*{'
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            match = re.search(component_pattern, line)
            if match:
                component_name = match.group(1)
                # Verifica se tem PropTypes definido
                if f'{component_name}.propTypes' not in content:
                    result.add_issue(self._create_issue(
                        file_path=file_path,
                        line_number=i + 1,
                        message=f"Componente '{component_name}' sem PropTypes",
                        description="Componentes React devem ter PropTypes ou TypeScript",
                        severity=Severity.MEDIUM,
                        category=IssueCategory.CODE_QUALITY,
                        rule_id="REACT004",
                        rule_name="Missing PropTypes",
                        suggestion="Adicione PropTypes ou migre para TypeScript"
                    ))
    
    def _check_react_keys(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica uso de keys em listas"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Procura por .map sem key
            if '.map(' in line:
                # Verifica se tem key nas próximas linhas
                has_key = False
                for j in range(i, min(i + 5, len(lines))):
                    if 'key=' in lines[j]:
                        has_key = True
                        break
                
                if not has_key and '<' in line:  # Renderiza JSX
                    result.add_issue(self._create_issue(
                        file_path=file_path,
                        line_number=i + 1,
                        message="Lista renderizada sem prop 'key'",
                        description="Elementos em listas devem ter prop 'key' única",
                        severity=Severity.HIGH,
                        category=IssueCategory.CODE_QUALITY,
                        rule_id="REACT005",
                        rule_name="Missing Key Prop",
                        suggestion="Adicione key={item.id} ou key={index} (evite index se possível)"
                    ))
    
    def _check_typescript_types(
        self,
        file_path: str,
        content: str,
        result: AnalysisResult
    ) -> None:
        """Verifica tipagem TypeScript"""
        lines = content.split('\n')
        
        # Funções sem tipo de retorno
        func_pattern = r'(?:function|const)\s+(\w+)\s*=?\s*\([^)]*\)\s*{'
        for i, line in enumerate(lines):
            match = re.search(func_pattern, line)
            if match and ':' not in line:  # Sem tipo de retorno
                func_name = match.group(1)
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=i + 1,
                    message=f"Função '{func_name}' sem tipo de retorno",
                    severity=Severity.LOW,
                    category=IssueCategory.CODE_QUALITY,
                    rule_id="TS001",
                    rule_name="Missing Return Type",
                    suggestion="Adicione tipo de retorno: (): ReturnType => {...}"
                ))
        
        # Uso de 'any'
        for i, line in enumerate(lines):
            if re.search(r':\s*any\b', line):
                result.add_issue(self._create_issue(
                    file_path=file_path,
                    line_number=i + 1,
                    message="Uso de tipo 'any' detectado",
                    description="Evite usar 'any', prefira tipos específicos",
                    severity=Severity.MEDIUM,
                    category=IssueCategory.CODE_QUALITY,
                    rule_id="TS002",
                    rule_name="Avoid Any Type",
                    suggestion="Defina um tipo ou interface específica"
                ))

# Made with Bob
