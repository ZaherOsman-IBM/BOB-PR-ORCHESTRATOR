"""
Analyzer Factory
Factory pattern para criar analisadores baseados no tipo de arquivo
"""

from typing import Dict, List, Any, Optional
from pathlib import Path

from .base_analyzer import BaseAnalyzer
from .swift_analyzer import SwiftAnalyzer
from .python_analyzer import PythonAnalyzer
from .java_analyzer import JavaAnalyzer
from .javascript_analyzer import JavaScriptAnalyzer


class AnalyzerFactory:
    """Factory para criar analisadores de código"""
    
    # Mapeamento de extensões para analisadores
    ANALYZER_MAP = {
        '.swift': SwiftAnalyzer,
        '.py': PythonAnalyzer,
        '.pyw': PythonAnalyzer,
        '.java': JavaAnalyzer,
        '.js': JavaScriptAnalyzer,
        '.jsx': JavaScriptAnalyzer,
        '.ts': JavaScriptAnalyzer,
        '.tsx': JavaScriptAnalyzer,
        '.mjs': JavaScriptAnalyzer,
        '.cjs': JavaScriptAnalyzer,
    }
    
    @classmethod
    def create_analyzer(
        cls,
        file_path: str,
        config: Dict[str, Any]
    ) -> Optional[BaseAnalyzer]:
        """
        Cria um analisador apropriado para o arquivo
        
        Args:
            file_path: Caminho do arquivo
            config: Configurações do analisador
            
        Returns:
            Instância do analisador ou None se não houver analisador disponível
        """
        extension = Path(file_path).suffix.lower()
        analyzer_class = cls.ANALYZER_MAP.get(extension)
        
        if analyzer_class:
            return analyzer_class(config)
        
        return None
    
    @classmethod
    def get_analyzer_for_language(
        cls,
        language: str,
        config: Dict[str, Any]
    ) -> Optional[BaseAnalyzer]:
        """
        Cria um analisador para uma linguagem específica
        
        Args:
            language: Nome da linguagem (swift, python, java, javascript)
            config: Configurações do analisador
            
        Returns:
            Instância do analisador ou None
        """
        language_map = {
            'swift': SwiftAnalyzer,
            'python': PythonAnalyzer,
            'java': JavaAnalyzer,
            'javascript': JavaScriptAnalyzer,
            'typescript': JavaScriptAnalyzer,
            'react': JavaScriptAnalyzer,
        }
        
        analyzer_class = language_map.get(language.lower())
        if analyzer_class:
            return analyzer_class(config)
        
        return None
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """
        Retorna lista de extensões suportadas
        
        Returns:
            Lista de extensões de arquivo
        """
        return list(cls.ANALYZER_MAP.keys())
    
    @classmethod
    def can_analyze(cls, file_path: str) -> bool:
        """
        Verifica se existe um analisador para o arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se pode analisar, False caso contrário
        """
        extension = Path(file_path).suffix.lower()
        return extension in cls.ANALYZER_MAP
    
    @classmethod
    def get_all_analyzers(cls, config: Dict[str, Any]) -> List[BaseAnalyzer]:
        """
        Cria instâncias de todos os analisadores disponíveis
        
        Args:
            config: Configurações dos analisadores
            
        Returns:
            Lista de analisadores
        """
        analyzers = []
        seen_classes = set()
        
        for analyzer_class in cls.ANALYZER_MAP.values():
            if analyzer_class not in seen_classes:
                analyzers.append(analyzer_class(config))
                seen_classes.add(analyzer_class)
        
        return analyzers

# Made with Bob
