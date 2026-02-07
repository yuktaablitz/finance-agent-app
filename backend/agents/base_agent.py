"""
Base Agent Class
All specialized agents inherit from this to ensure consistent output format
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from models.agent_models import (
    UserContext, 
    AgentResponse, 
    AgentMetadata,
    AgentType
)
from agents.personalities import get_personality_prompt
from agents.context_analyzer import ContextAnalyzer
from services.gemini_service import gemini_service


class BaseAgent(ABC):
    """
    Base class for all financial agents.
    ENSURES STANDARDIZED OUTPUT FORMAT across all agents.
    """
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
    
    def _build_system_prompt(
        self, 
        user_context: UserContext,
        context_analyzer: ContextAnalyzer
    ) -> str:
        """Build the complete system prompt with personality and context."""
        
        # Get personality instruction
        personality_prompt = get_personality_prompt(user_context.financial_personality)
        
        # Get context analysis
        context_prompt = context_analyzer.get_context_prompt_addition()
        
        # Get agent-specific instructions
        agent_instructions = self._get_agent_instructions()
        
        base_prompt = f"""You are a specialized financial AI assistant focused on {self.agent_type.value} advice.

YOUR CORE ROLE:
{agent_instructions}

YOUR PERSONALITY:
{personality_prompt}

CURRENT CONTEXT:
{context_prompt}

USER FINANCIAL SNAPSHOT:
- Current Balance: ${user_context.current_balance:.2f}
- Monthly Income: ${user_context.monthly_income:.2f}
- Monthly Budget: ${user_context.monthly_budget:.2f}
- Payday: Day {user_context.payday_day} of each month

CRITICAL RULES:
1. Always provide actionable advice, not just information
2. Reference specific numbers when possible
3. Consider the timing context (payday proximity, month-end) in your advice
4. Stay true to your assigned personality throughout
5. Be concise but complete
6. ALWAYS return valid JSON in the exact format specified

OUTPUT FORMAT:
You MUST respond with valid JSON only, matching this structure exactly:
{{
    "response": "your conversational response here",
    "metadata": {{
        "agent": "{self.agent_type.value}",
        "confidence": 0.0 to 1.0,
        "personality_used": "{user_context.financial_personality}",
        "context_factors": ["list", "of", "relevant", "factors"],
        "suggested_action": "specific_action_or_null",
        "related_transactions": ["txn_id1", "txn_id2"] or null
    }}
}}"""
        
        return base_prompt
    
    @abstractmethod
    def _get_agent_instructions(self) -> str:
        """Return agent-specific instructions. Must be implemented by subclasses."""
        pass
    
    async def process(
        self,
        query: str,
        user_context: UserContext,
        transaction_context: Optional[List[Dict[str, Any]]] = None
    ) -> AgentResponse:
        """
        Process a query and return standardized AgentResponse.
        This is the MAIN method all agents use.
        """
        # Analyze context
        context_analyzer = ContextAnalyzer(user_context)
        context_analysis = context_analyzer.analyze()
        
        # Build system prompt
        system_prompt = self._build_system_prompt(user_context, context_analyzer)
        
        # Add transaction context if available
        if transaction_context:
            tx_info = f"\n\nRECENT TRANSACTIONS:\n{self._format_transactions(transaction_context)}"
            query = query + tx_info
        
        # Generate response via Gemini
        result = await gemini_service.generate_response(
            system_prompt=system_prompt,
            user_query=query,
            temperature=0.7
        )
        
        # Ensure standardized output
        return self._standardize_response(result, context_analyzer, user_context)
    
    def _format_transactions(self, transactions: List[Dict[str, Any]]) -> str:
        """Format transactions for prompt context."""
        formatted = []
        for tx in transactions[:5]:  # Limit to 5 most recent
            formatted.append(
                f"- {tx.get('date', 'Unknown')}: {tx.get('merchant', 'Unknown')} "
                f"${abs(tx.get('amount', 0)):.2f} ({tx.get('category', 'uncategorized')})"
            )
        return "\n".join(formatted)
    
    def _standardize_response(
        self, 
        result: Dict,
        context_analyzer: ContextAnalyzer,
        user_context: UserContext
    ) -> AgentResponse:
        """
        Ensure the response matches AgentResponse structure exactly.
        This guarantees ALL agents return consistent format.
        """
        response_text = result.get("response", "I apologize, I couldn't process that request.")
        metadata = result.get("metadata", {})
        
        # Get context factors
        context_factors = context_analyzer.get_context_factors()
        
        # Build standardized metadata
        standardized_metadata = AgentMetadata(
            agent=metadata.get("agent", self.agent_type.value),
            confidence=metadata.get("confidence", 0.7),
            personality_used=metadata.get("personality_used", user_context.financial_personality),
            context_factors=metadata.get("context_factors", context_factors) or context_factors,
            suggested_action=metadata.get("suggested_action"),
            related_transactions=metadata.get("related_transactions")
        )
        
        return AgentResponse(
            response=response_text,
            metadata=standardized_metadata
        )
