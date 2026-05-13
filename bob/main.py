"""
BOB Main Orchestrator
Orquestrador principal que coordena análise de PRs e notificações
"""

import argparse
import sys
import json
import yaml
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import gitlab

from .analyzers.analyzer_factory import AnalyzerFactory
from .analyzers.base_analyzer import AnalysisResult, Issue, Severity
from .compliance.security_checker import SecurityChecker
from .reporters.slack_notifier import SlackNotifier


class BOBOrchestrator:
    """Orquestrador principal do BOB"""
    
    def __init__(
        self,
        gitlab_url: str,
        gitlab_token: str,
        config_path: str,
        slack_config_path: str
    ):
        """
        Inicializa o orquestrador
        
        Args:
            gitlab_url: URL do GitLab
            gitlab_token: Token de acesso GitLab
            config_path: Caminho para arquivo de configuração
            slack_config_path: Caminho para configuração Slack
        """
        self.gitlab_url = gitlab_url
        self.gitlab_token = gitlab_token
        
        # Carrega configurações
        self.config = self._load_config(config_path)
        self.slack_config = self._load_config(slack_config_path)
        
        # Inicializa componentes
        self.gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
        self.security_checker = SecurityChecker(self.config)
        self.slack_notifier = SlackNotifier(self.slack_config)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carrega arquivo de configuração YAML"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar configuração {config_path}: {e}")
            return {}
    
    def analyze_pull_request(
        self,
        project_id: int,
        pr_id: int
    ) -> Dict[str, Any]:
        """
        Analisa um Pull Request completo
        
        Args:
            project_id: ID do projeto GitLab
            pr_id: ID do Pull Request
            
        Returns:
            Resultado da análise
        """
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"🤖 BOB - Analisando Pull Request #{pr_id}")
        print(f"{'='*60}\n")
        
        try:
            # Obtém informações do PR
            project = self.gl.projects.get(project_id)
            mr = project.mergerequests.get(pr_id)
            
            pr_info = {
                'iid': mr.iid,
                'title': mr.title,
                'description': mr.description,
                'author': mr.author['username'],
                'reviewer': mr.assignee['username'] if mr.assignee else 'Não atribuído',
                'web_url': mr.web_url,
                'source_branch': mr.source_branch,
                'target_branch': mr.target_branch,
                'state': mr.state
            }
            
            print(f"📋 PR: {pr_info['title']}")
            print(f"👤 Autor: {pr_info['author']}")
            print(f"👁️  Revisor: {pr_info['reviewer']}")
            print(f"🔗 URL: {pr_info['web_url']}\n")
            
            # Obtém arquivos modificados
            changes = mr.changes()
            modified_files = [change['new_path'] for change in changes['changes']]
            
            print(f"📁 Arquivos modificados: {len(modified_files)}\n")
            
            # Analisa arquivos
            analysis_results = []
            all_issues = []
            
            for file_path in modified_files:
                print(f"  🔍 Analisando: {file_path}")
                
                # Cria analisador apropriado
                analyzer = AnalyzerFactory.create_analyzer(file_path, self.config)
                
                if analyzer:
                    try:
                        # Obtém conteúdo do arquivo
                        file_content = self._get_file_content(project, mr, file_path)
                        
                        # Análise de código
                        result = analyzer.analyze_file(file_path)
                        analysis_results.append(result)
                        all_issues.extend(result.issues)
                        
                        # Verificação de segurança
                        security_issues = self.security_checker.check_file(
                            file_path,
                            file_content
                        )
                        all_issues.extend(security_issues)
                        
                        print(f"    ✓ {len(result.issues)} issues de código")
                        print(f"    ✓ {len(security_issues)} issues de segurança")
                        
                    except Exception as e:
                        print(f"    ⚠️  Erro: {str(e)}")
                else:
                    print(f"    ⊘ Sem analisador disponível")
            
            # Resumo da análise
            print(f"\n{'='*60}")
            print("📊 RESUMO DA ANÁLISE")
            print(f"{'='*60}\n")
            
            summary = self._generate_summary(analysis_results, all_issues)
            self._print_summary(summary)
            
            # Verifica se deve bloquear PR
            should_block = self._should_block_pr(all_issues)
            
            if should_block:
                print("\n🔴 PR BLOQUEADO - Erros críticos encontrados!")
            else:
                print("\n✅ PR APROVADO pelo BOB - Pode prosseguir para revisão humana")
            
            # Envia notificação Slack
            print(f"\n{'='*60}")
            print("📤 ENVIANDO NOTIFICAÇÃO SLACK")
            print(f"{'='*60}\n")
            
            pr_info['report_url'] = f"{mr.web_url}/-/jobs/artifacts"
            
            slack_sent = self.slack_notifier.notify_pr_analysis(
                pr_info,
                analysis_results,
                all_issues
            )
            
            if slack_sent:
                print("✅ Notificação enviada com sucesso!")
            else:
                print("⚠️  Notificação não enviada (verifique configuração)")
            
            # Prepara resultado final
            execution_time = time.time() - start_time
            
            result = {
                'pr_info': pr_info,
                'summary': summary,
                'analysis_results': [r.to_dict() for r in analysis_results],
                'all_issues': [i.to_dict() for i in all_issues],
                'should_block': should_block,
                'execution_time': execution_time,
                'slack_notified': slack_sent
            }
            
            print(f"\n⏱️  Tempo de execução: {execution_time:.2f}s")
            print(f"\n{'='*60}\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ ERRO FATAL: {str(e)}\n")
            
            # Notifica erro no Slack
            try:
                self.slack_notifier.notify_error(
                    {'iid': pr_id, 'title': 'Erro na análise'},
                    str(e)
                )
            except:
                pass
            
            raise
    
    def _get_file_content(
        self,
        project,
        mr,
        file_path: str
    ) -> str:
        """Obtém conteúdo de um arquivo do PR"""
        try:
            file_obj = project.files.get(
                file_path=file_path,
                ref=mr.source_branch
            )
            return file_obj.decode().decode('utf-8')
        except Exception as e:
            print(f"    ⚠️  Não foi possível ler arquivo: {e}")
            return ""
    
    def _generate_summary(
        self,
        analysis_results: List[AnalysisResult],
        all_issues: List[Issue]
    ) -> Dict[str, Any]:
        """Gera resumo da análise"""
        return {
            'total_files': sum(r.total_files for r in analysis_results),
            'total_lines': sum(r.total_lines for r in analysis_results),
            'total_issues': len(all_issues),
            'critical': len([i for i in all_issues if i.severity == Severity.CRITICAL]),
            'high': len([i for i in all_issues if i.severity == Severity.HIGH]),
            'medium': len([i for i in all_issues if i.severity == Severity.MEDIUM]),
            'low': len([i for i in all_issues if i.severity == Severity.LOW]),
            'info': len([i for i in all_issues if i.severity == Severity.INFO]),
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
    
    def _should_block_pr(self, issues: List[Issue]) -> bool:
        """Determina se o PR deve ser bloqueado"""
        # Bloqueia se houver issues críticos
        critical_issues = [i for i in issues if i.severity == Severity.CRITICAL]
        
        if critical_issues:
            return True
        
        # Verifica configuração de segurança
        security_issues = [i for i in issues if i.category.value == 'security']
        if security_issues and self.security_checker.should_block_pr(security_issues):
            return True
        
        return False
    
    def save_report(self, result: Dict[str, Any], output_path: str) -> None:
        """Salva relatório em arquivo JSON"""
        try:
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"💾 Relatório salvo em: {output_path}")
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='BOB - Pull Request Orchestrator and Code Compliance'
    )
    
    parser.add_argument(
        '--pr-id',
        type=int,
        required=True,
        help='ID do Pull Request'
    )
    
    parser.add_argument(
        '--project-id',
        type=int,
        required=True,
        help='ID do projeto GitLab'
    )
    
    parser.add_argument(
        '--gitlab-url',
        type=str,
        required=True,
        help='URL do GitLab'
    )
    
    parser.add_argument(
        '--gitlab-token',
        type=str,
        required=True,
        help='Token de acesso GitLab'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/ibm_policies.yaml',
        help='Caminho para arquivo de configuração'
    )
    
    parser.add_argument(
        '--slack-config',
        type=str,
        default='config/slack_config.yaml',
        help='Caminho para configuração Slack'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='bob-report.json',
        help='Caminho para salvar relatório'
    )
    
    args = parser.parse_args()
    
    try:
        # Inicializa orquestrador
        bob = BOBOrchestrator(
            gitlab_url=args.gitlab_url,
            gitlab_token=args.gitlab_token,
            config_path=args.config,
            slack_config_path=args.slack_config
        )
        
        # Analisa PR
        result = bob.analyze_pull_request(
            project_id=args.project_id,
            pr_id=args.pr_id
        )
        
        # Salva relatório
        bob.save_report(result, args.output)
        
        # Retorna código de saída baseado no resultado
        if result['should_block']:
            print("\n❌ Análise concluída com ERROS CRÍTICOS")
            sys.exit(1)
        else:
            print("\n✅ Análise concluída com SUCESSO")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {str(e)}")
        sys.exit(2)


if __name__ == '__main__':
    main()

# Made with Bob
