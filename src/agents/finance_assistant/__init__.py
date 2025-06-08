"""
Finance Assistant Agent

A specialized agent for analyzing financial data using the OpenGov FIN GraphQL API.
It uses a dual-model approach with LangGraph nodes:
- Tool Node: o4-mini-2025-04-16 for GraphQL queries and tool execution
- Chat Node: gpt-4o for conversational responses and analysis
"""

from .graph import create_finance_agent
from .utils import run_finance_assistant, get_finance_agent as get_finance_assistant

__all__ = ["create_finance_agent", "run_finance_assistant", "get_finance_assistant"] 