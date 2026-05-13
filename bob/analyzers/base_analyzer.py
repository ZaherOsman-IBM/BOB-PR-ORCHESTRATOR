"""
Base Analyzer Class
Classe base abstrata para todos os analisadores de código
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from pathlib import Path


class Severity(Enum):
    """Níveis de severidade dos problemas encontrados"""
    CRITICAL = "CRITICAL"  # Bloqueia PR
    HIGH = "HIGH"          # Requer atenção imediata
    MEDIUM = "MEDIUM"      # Deve ser corrigido
    LOW = "LOW"            # Sugestão de melhoria
    INFO = "INFO"          # Informativo


class IssueCategory(Enum):
    """Categorias de problemas"""
    SECURITY = "security"
    ARCHITECTURE = "architecture"
    CODE_QUALITY = "code_quality"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    STYLE = "style"


@dataclass
class Issue:
    """Representa um problema encontrado no código"""
    
    # Identificação
    file_path: str
    line_number: int
    column: Optional[int] = None
    
    # Classificação
    severity: Severity = Severity.MEDIUM
    category: IssueCategory = IssueCategory.CODE_QUALITY
    
    # Descrição
    message: str = ""
    description: str = ""
    code_snippet: Optional[str] = None
    
    # Contexto
    rule_id: Optional[str] = None
    rule_name: Optional[str] = None
    
    # Solução
    suggestion: Optional[str] = None
    fix_available: bool = False
    auto_fixable: bool = False
    
    # Links
    documentation_url: Optional[str] = None
    
    # Metadados
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o issue para dicionário"""
        return {
            'file_path': self.file_path,
            'line_number': self.line_number,
            'column': self.column,
            'severity': self.severity.value,
            'category': self.category.value,
            'message': self.message,
            'description': self.description,
            'code_snippet': self.code_snippet,
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'suggestion': self.suggestion,
            'fix_available': self.fix_available,
            'auto_fixable': self.auto_fixable,
            'documentation_url': self.documentation_url,
            'metadata': self.metadata
        }
    
    def is_blocking(self) -> bool:
        """Verifica se o issue bloqueia o PR"""
        return self.severity == Severity.CRITICAL


@dataclass
class AnalysisResult:
    """Resultado da análise de um arquivo ou conjunto de arquivos"""
    
    # Identificação
    analyzer_name: str
    language: str
    
    # Arquivos analisados
    files_analyzed: List[str] = field(default_factory=list)
    
    # Problemas encontrados
    issues: List[Issue] = field(default_factory=list)
    
    # Estatísticas
    total_lines: int = 0
    total_files: int = 0
    
    # Status
    success: bool = True
    error_message: Optional[str] = None
    
    # Tempo de execução
    execution_time: float = 0.0
    
    # Metadados
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_issue(self, issue: Issue) -> None:
        """Adiciona um issue ao resultado"""
        self.issues.append(issue)
    
    def get_issues_by_severity(self, severity: Severity) -> List[Issue]:
        """Retorna issues de uma severidade específica"""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_critical_issues(self) -> List[Issue]:
        """Retorna apenas issues críticos"""
        return self.get_issues_by_severity(Severity.CRITICAL)
    
    def has_blocking_issues(self) -> bool:
        """Verifica se há issues que bloqueiam o PR"""
        return len(self.get_critical_issues()) > 0
    
    def get_issues_by_category(self, category: IssueCategory) -> List[Issue]:
        """Retorna issues de uma categoria específica"""
        return [issue for issue in self.issues if issue.category == category]
    
    def get_summary(self) -> Dict[str, int]:
        """Retorna resumo dos issues por severidade"""
        return {
            'critical': len(self.get_issues_by_severity(Severity.CRITICAL)),
            'high': len(self.get_issues_by_severity(Severity.HIGH)),
            'medium': len(self.get_issues_by_severity(Severity.MEDIUM)),
            'low': len(self.get_issues_by_severity(Severity.LOW)),
            'info': len(self.get_issues_by_severity(Severity.INFO)),
            'total': len(self.issues)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o resultado para dicionário"""
        return {
            'analyzer_name': self.analyzer_name,
            'language': self.language,
            'files_analyzed': self.files_analyzed,
            'issues': [issue.to_dict() for issue in self.issues],
            'total_lines': self.total_lines,
            'total_files': self.total_files,
            'success': self.success,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'summary': self.get_summary(),
            'has_blocking_issues': self.has_blocking_issues(),
            'metadata': self.metadata
        }


class BaseAnalyzer(ABC):
    """
    Classe base abstrata para todos os analisadores de código.
    Cada linguagem deve implementar sua própria classe derivada.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o analisador
        
        Args:
            config: Configurações do analisador
        """
        self.config = config
        self.name = self.__class__.__name__
        self.language = self._get_language()
    
    @abstractmethod
    def _get_language(self) -> str:
        """Retorna o nome da linguagem analisada"""
        pass
    
    @abstractmethod
    def can_analyze(self, file_path: str) -> bool:
        """
        Verifica se o analisador pode analisar o arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se pode analisar, False caso contrário
        """
        pass
    
    @abstractmethod
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        Analisa um arquivo específico
        
        Args:
            file_path: Caminho do arquivo a ser analisado
            
        Returns:
            Resultado da análise
        """
        pass
    
    def analyze_files(self, file_paths: List[str]) -> AnalysisResult:
        """
        Analisa múltiplos arquivos
        
        Args:
            file_paths: Lista de caminhos de arquivos
            
        Returns:
            Resultado consolidado da análise
        """
        result = AnalysisResult(
            analyzer_name=self.name,
            language=self.language
        )
        
        for file_path in file_paths:
            if self.can_analyze(file_path):
                file_result = self.analyze_file(file_path)
                result.issues.extend(file_result.issues)
                result.files_analyzed.append(file_path)
                result.total_lines += file_result.total_lines
        
        result.total_files = len(result.files_analyzed)
        return result
    
    def _read_file(self, file_path: str) -> str:
        """
        Lê o conteúdo de um arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Conteúdo do arquivo
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Erro ao ler arquivo {file_path}: {str(e)}")
    
    def _count_lines(self, file_path: str) -> int:
        """
        Conta o número de linhas de um arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Número de linhas
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    def _get_file_extension(self, file_path: str) -> str:
        """
        Retorna a extensão do arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Extensão do arquivo (sem o ponto)
        """
        return Path(file_path).suffix.lstrip('.')
    
    def _create_issue(
        self,
        file_path: str,
        line_number: int,
        message: str,
        severity: Severity = Severity.MEDIUM,
        category: IssueCategory = IssueCategory.CODE_QUALITY,
        **kwargs
    ) -> Issue:
        """
        Cria um novo issue
        
        Args:
            file_path: Caminho do arquivo
            line_number: Número da linha
            message: Mensagem do problema
            severity: Severidade do problema
            category: Categoria do problema
            **kwargs: Argumentos adicionais para o Issue
            
        Returns:
            Issue criado
        """
        return Issue(
            file_path=file_path,
            line_number=line_number,
            message=message,
            severity=severity,
            category=category,
            **kwargs
        )

# Made with Bob
