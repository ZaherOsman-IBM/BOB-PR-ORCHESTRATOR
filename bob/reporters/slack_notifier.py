"""
Slack Notifier
Envia notificações para o Slack sobre análises de PR
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from ..analyzers.base_analyzer import Issue, Severity, AnalysisResult


class SlackNotifier:
    """Notificador para Slack"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o notificador Slack
        
        Args:
            config: Configurações do Slack
        """
        self.config = config
        
        # Obtém token do ambiente ou config
        bot_token = os.getenv('SLACK_BOT_TOKEN') or config.get('bot_token', '')
        self.client = WebClient(token=bot_token) if bot_token else None
        
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL') or config.get('webhook_url', '')
        self.default_channel = config.get('default_channel', '#code-reviews')
        self.emojis = config.get('emojis', {})
        self.user_mapping = config.get('user_mapping', {})
    
    def notify_pr_analysis(
        self,
        pr_info: Dict[str, Any],
        analysis_results: List[AnalysisResult],
        all_issues: List[Issue]
    ) -> bool:
        """
        Envia notificação sobre análise de PR
        
        Args:
            pr_info: Informações do Pull Request
            analysis_results: Resultados das análises
            all_issues: Todos os issues encontrados
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        # Determina severidade geral
        has_critical = any(i.severity == Severity.CRITICAL for i in all_issues)
        has_high = any(i.severity == Severity.HIGH for i in all_issues)
        
        # Escolhe template baseado na severidade
        if has_critical:
            template = 'pr_blocked'
            channel = self.config.get('channels', {}).get('critical', self.default_channel)
        elif has_high:
            template = 'pr_warning'
            channel = self.config.get('channels', {}).get('general', self.default_channel)
        else:
            template = 'pr_approved'
            channel = self.config.get('channels', {}).get('general', self.default_channel)
        
        # Constrói mensagem
        message = self._build_message(pr_info, analysis_results, all_issues, template)
        
        # Envia mensagem
        return self._send_message(channel, message)
    
    def _build_message(
        self,
        pr_info: Dict[str, Any],
        analysis_results: List[AnalysisResult],
        all_issues: List[Issue],
        template: str
    ) -> Dict[str, Any]:
        """Constrói mensagem formatada para Slack"""
        
        # Conta issues por severidade
        critical_count = sum(1 for i in all_issues if i.severity == Severity.CRITICAL)
        high_count = sum(1 for i in all_issues if i.severity == Severity.HIGH)
        medium_count = sum(1 for i in all_issues if i.severity == Severity.MEDIUM)
        low_count = sum(1 for i in all_issues if i.severity == Severity.LOW)
        
        # Conta arquivos analisados
        total_files = sum(r.total_files for r in analysis_results)
        
        # Obtém template config
        template_config = self.config.get('templates', {}).get(template, {})
        title = template_config.get('title', '🤖 BOB - Análise de Pull Request')
        color = template_config.get('color', '#808080')
        
        # Mapeia usuários GitLab para Slack
        developer = pr_info.get('author', 'Unknown')
        reviewer = pr_info.get('reviewer', 'Unknown')
        developer_slack = self._map_user(developer)
        reviewer_slack = self._map_user(reviewer)
        
        # Constrói blocos da mensagem
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title,
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*PR #{pr_info.get('iid', 'N/A')}*: {pr_info.get('title', 'Sem título')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Link*: <{pr_info.get('web_url', '#')}|Ver PR>"
                    }
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Desenvolvedor*: {developer_slack}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Revisor*: {reviewer_slack}"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📊 Resultado da Análise*\n• ✅ {total_files - len(all_issues)} arquivos sem problemas\n• 🔴 {critical_count} erros críticos\n• ⚠️ {high_count + medium_count} avisos\n• 💡 {low_count} sugestões"
                }
            }
        ]
        
        # Adiciona issues críticos
        if critical_count > 0:
            critical_issues = [i for i in all_issues if i.severity == Severity.CRITICAL][:5]
            critical_text = "*🔴 Erros Críticos* (PR bloqueado):\n"
            for idx, issue in enumerate(critical_issues, 1):
                critical_text += f"{idx}. `{issue.file_path}:{issue.line_number}` - {issue.message}\n"
            
            if critical_count > 5:
                critical_text += f"\n_...e mais {critical_count - 5} erros críticos_"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": critical_text
                }
            })
        
        # Adiciona avisos importantes
        if high_count > 0:
            high_issues = [i for i in all_issues if i.severity == Severity.HIGH][:3]
            warning_text = "*⚠️ Avisos Importantes*:\n"
            for idx, issue in enumerate(high_issues, 1):
                warning_text += f"{idx}. `{issue.file_path}:{issue.line_number}` - {issue.message}\n"
            
            if high_count > 3:
                warning_text += f"\n_...e mais {high_count - 3} avisos_"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": warning_text
                }
            })
        
        # Adiciona próximos passos
        blocks.append({
            "type": "divider"
        })
        
        if critical_count > 0:
            next_steps = f"*📝 Próximos Passos*:\n{developer_slack} precisa corrigir os erros críticos antes da revisão humana."
        elif high_count > 0:
            next_steps = f"*📝 Próximos Passos*:\n{developer_slack} deve revisar os avisos. {reviewer_slack} pode iniciar a revisão."
        else:
            next_steps = f"*📝 Próximos Passos*:\n✅ Código aprovado pelo BOB! {reviewer_slack} pode revisar o PR."
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": next_steps
            }
        })
        
        # Adiciona botão para relatório completo
        if pr_info.get('report_url'):
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📄 Ver Relatório Completo",
                            "emoji": True
                        },
                        "url": pr_info['report_url'],
                        "style": "primary"
                    }
                ]
            })
        
        return {
            "blocks": blocks,
            "attachments": [
                {
                    "color": color,
                    "footer": f"BOB - Análise realizada em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                    "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png"
                }
            ]
        }
    
    def _map_user(self, gitlab_username: str) -> str:
        """
        Mapeia usuário GitLab para menção Slack
        
        Args:
            gitlab_username: Username do GitLab
            
        Returns:
            Menção Slack formatada ou username original
        """
        slack_id = self.user_mapping.get(gitlab_username)
        if slack_id:
            return f"<@{slack_id}>"
        return f"@{gitlab_username}"
    
    def _send_message(self, channel: str, message: Dict[str, Any]) -> bool:
        """
        Envia mensagem para o Slack
        
        Args:
            channel: Canal de destino
            message: Mensagem formatada
            
        Returns:
            True se enviou com sucesso
        """
        if not self.client:
            print("⚠️ Slack client não configurado. Mensagem não enviada.")
            print(f"Canal: {channel}")
            print(f"Mensagem: {json.dumps(message, indent=2)}")
            return False
        
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                **message
            )
            return response['ok']
        except SlackApiError as e:
            print(f"❌ Erro ao enviar mensagem para Slack: {e.response['error']}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado ao enviar mensagem: {str(e)}")
            return False
    
    def notify_error(self, pr_info: Dict[str, Any], error_message: str) -> bool:
        """
        Notifica sobre erro na análise
        
        Args:
            pr_info: Informações do PR
            error_message: Mensagem de erro
            
        Returns:
            True se enviou com sucesso
        """
        channel = self.config.get('channels', {}).get('critical', self.default_channel)
        
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "❌ BOB - Erro na Análise",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*PR #{pr_info.get('iid', 'N/A')}*: {pr_info.get('title', 'Sem título')}\n\n*Erro*: {error_message}"
                    }
                }
            ]
        }
        
        return self._send_message(channel, message)

# Made with Bob
