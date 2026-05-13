"""
Security Checker
Verificador de segurança - detecta credenciais, secrets e vulnerabilidades
"""

import re
from typing import List, Dict, Any
from pathlib import Path

from ..analyzers.base_analyzer import Issue, Severity, IssueCategory


class SecurityChecker:
    """Verificador de segurança para código"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o verificador de segurança
        
        Args:
            config: Configurações de segurança
        """
        self.config = config
        self.security_config = config.get('security', {})
        self.forbidden_patterns = self.security_config.get('forbidden_patterns', [])
    
    def check_file(self, file_path: str, content: str) -> List[Issue]:
        """
        Verifica um arquivo em busca de problemas de segurança
        
        Args:
            file_path: Caminho do arquivo
            content: Conteúdo do arquivo
            
        Returns:
            Lista de issues encontrados
        """
        issues = []
        
        # Verifica padrões proibidos (credenciais, secrets, etc)
        issues.extend(self._check_forbidden_patterns(file_path, content))
        
        # Verifica AWS credentials
        issues.extend(self._check_aws_credentials(file_path, content))
        
        # Verifica strings de conexão de banco de dados
        issues.extend(self._check_database_connections(file_path, content))
        
        # Verifica tokens e API keys
        issues.extend(self._check_tokens(file_path, content))
        
        # Verifica uso de eval/exec (Python)
        if file_path.endswith('.py'):
            issues.extend(self._check_dangerous_functions(file_path, content))
        
        return issues
    
    def _check_forbidden_patterns(
        self,
        file_path: str,
        content: str
    ) -> List[Issue]:
        """Verifica padrões proibidos configurados"""
        issues = []
        
        for pattern_config in self.forbidden_patterns:
            pattern = pattern_config.get('pattern', '')
            message = pattern_config.get('message', 'Padrão proibido detectado')
            severity_str = pattern_config.get('severity', 'CRITICAL')
            
            try:
                severity = Severity[severity_str]
            except KeyError:
                severity = Severity.CRITICAL
            
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                # Extrai snippet do código
                lines = content.split('\n')
                code_snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                
                issues.append(Issue(
                    file_path=file_path,
                    line_number=line_num,
                    message=message,
                    description=f"Padrão de segurança violado: {pattern}",
                    code_snippet=code_snippet,
                    severity=severity,
                    category=IssueCategory.SECURITY,
                    rule_id="SEC001",
                    rule_name="Forbidden Pattern Detected",
                    suggestion="Remova a credencial/secret e use um gerenciador de secrets aprovado"
                ))
        
        return issues
    
    def _check_aws_credentials(
        self,
        file_path: str,
        content: str
    ) -> List[Issue]:
        """Verifica credenciais AWS expostas"""
        issues = []
        
        # AWS Access Key ID pattern
        aws_key_pattern = r'AKIA[0-9A-Z]{16}'
        matches = re.finditer(aws_key_pattern, content)
        
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            lines = content.split('\n')
            code_snippet = lines[line_num - 1] if line_num <= len(lines) else ""
            
            issues.append(Issue(
                file_path=file_path,
                line_number=line_num,
                message="AWS Access Key ID detectada",
                description="Credencial AWS exposta no código",
                code_snippet=code_snippet,
                severity=Severity.CRITICAL,
                category=IssueCategory.SECURITY,
                rule_id="SEC002",
                rule_name="AWS Credentials Exposed",
                suggestion="Use AWS Secrets Manager ou variáveis de ambiente",
                documentation_url="https://docs.aws.amazon.com/secretsmanager/"
            ))
        
        # AWS Secret Access Key pattern (mais genérico)
        secret_pattern = r'(?i)aws[_-]?secret[_-]?(?:access[_-]?)?key[\'"\s]*[:=][\'"\s]*([A-Za-z0-9/+=]{40})'
        matches = re.finditer(secret_pattern, content)
        
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            lines = content.split('\n')
            code_snippet = lines[line_num - 1] if line_num <= len(lines) else ""
            
            issues.append(Issue(
                file_path=file_path,
                line_number=line_num,
                message="AWS Secret Access Key detectada",
                description="Secret key AWS exposta no código",
                code_snippet=code_snippet,
                severity=Severity.CRITICAL,
                category=IssueCategory.SECURITY,
                rule_id="SEC003",
                rule_name="AWS Secret Key Exposed"
            ))
        
        return issues
    
    def _check_database_connections(
        self,
        file_path: str,
        content: str
    ) -> List[Issue]:
        """Verifica strings de conexão de banco de dados expostas"""
        issues = []
        
        # Padrões de connection strings
        db_patterns = [
            (r'mongodb(\+srv)?://[^/\s]+', 'MongoDB'),
            (r'postgres://[^/\s]+', 'PostgreSQL'),
            (r'mysql://[^/\s]+', 'MySQL'),
            (r'redis://[^/\s]+', 'Redis'),
            (r'Server=.+;Database=.+;User Id=.+;Password=.+', 'SQL Server'),
        ]
        
        for pattern, db_type in db_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                lines = content.split('\n')
                code_snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                
                issues.append(Issue(
                    file_path=file_path,
                    line_number=line_num,
                    message=f"String de conexão {db_type} exposta",
                    description="Connection string com credenciais no código",
                    code_snippet=code_snippet,
                    severity=Severity.CRITICAL,
                    category=IssueCategory.SECURITY,
                    rule_id="SEC004",
                    rule_name="Database Connection String Exposed",
                    suggestion="Use variáveis de ambiente ou secrets manager"
                ))
        
        return issues
    
    def _check_tokens(
        self,
        file_path: str,
        content: str
    ) -> List[Issue]:
        """Verifica tokens e API keys expostos"""
        issues = []
        
        # Padrões de tokens
        token_patterns = [
            (r'(?i)bearer[\'"\s]+[A-Za-z0-9\-._~+/]+=*', 'Bearer Token'),
            (r'(?i)token[\'"\s]*[:=][\'"\s]*[A-Za-z0-9\-._~+/]{20,}', 'Generic Token'),
            (r'(?i)api[_-]?key[\'"\s]*[:=][\'"\s]*[A-Za-z0-9\-._~+/]{20,}', 'API Key'),
            (r'ghp_[A-Za-z0-9]{36}', 'GitHub Personal Access Token'),
            (r'gho_[A-Za-z0-9]{36}', 'GitHub OAuth Token'),
            (r'sk-[A-Za-z0-9]{48}', 'OpenAI API Key'),
        ]
        
        for pattern, token_type in token_patterns:
            matches = re.finditer(pattern, content)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                lines = content.split('\n')
                code_snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                
                issues.append(Issue(
                    file_path=file_path,
                    line_number=line_num,
                    message=f"{token_type} detectado",
                    description="Token/API Key exposto no código",
                    code_snippet=code_snippet,
                    severity=Severity.CRITICAL,
                    category=IssueCategory.SECURITY,
                    rule_id="SEC005",
                    rule_name="Token/API Key Exposed",
                    suggestion="Use secrets manager ou variáveis de ambiente"
                ))
        
        return issues
    
    def _check_dangerous_functions(
        self,
        file_path: str,
        content: str
    ) -> List[Issue]:
        """Verifica uso de funções perigosas em Python"""
        issues = []
        
        dangerous_functions = [
            ('eval', 'Permite execução de código arbitrário'),
            ('exec', 'Permite execução de código arbitrário'),
            ('compile', 'Pode ser usado para executar código malicioso'),
            ('__import__', 'Import dinâmico pode ser perigoso'),
            ('pickle.loads', 'Desserialização insegura'),
            ('yaml.load', 'Use yaml.safe_load ao invés'),
        ]
        
        for func, description in dangerous_functions:
            pattern = rf'\b{re.escape(func)}\s*\('
            matches = re.finditer(pattern, content)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                lines = content.split('\n')
                code_snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                
                issues.append(Issue(
                    file_path=file_path,
                    line_number=line_num,
                    message=f"Uso de função perigosa: {func}()",
                    description=description,
                    code_snippet=code_snippet,
                    severity=Severity.HIGH,
                    category=IssueCategory.SECURITY,
                    rule_id="SEC006",
                    rule_name="Dangerous Function Usage",
                    suggestion=f"Evite usar {func}() ou valide rigorosamente a entrada"
                ))
        
        return issues
    
    def should_block_pr(self, issues: List[Issue]) -> bool:
        """
        Verifica se os issues de segurança devem bloquear o PR
        
        Args:
            issues: Lista de issues de segurança
            
        Returns:
            True se deve bloquear, False caso contrário
        """
        if not self.security_config.get('block_on_credentials', True):
            return False
        
        # Bloqueia se houver qualquer issue crítico de segurança
        return any(
            issue.severity == Severity.CRITICAL and 
            issue.category == IssueCategory.SECURITY 
            for issue in issues
        )

# Made with Bob
