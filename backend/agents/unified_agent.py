"""
Unified Agent Router
Single agent bar that routes to specialized sub-agents based on query content
Maintains stateful context across all agent switches
"""

import re
from typing import Dict, List, Optional, Any
from models.agent_models import (
    UserContext, 
    AgentQuery, 
    AgentResponse, 
    AgentType
)
from agents.spending_agent import SpendingAgent
from agents.investing_agent import InvestingAgent
from agents.savings_agent import SavingsAgent
from agents.budget_agent import BudgetAgent
from agents.base_agent import BaseAgent
from agents.context_analyzer import ContextAnalyzer


class UnifiedAgentRouter:
    """
    UNIFIED AGENT BAR - Single entry point for all agent queries
    
    This router:
    1. Analyzes user query to determine which agent should handle it
    2. Routes to the appropriate specialized agent
    3. Maintains session state across agent switches
    4. Returns standardized AgentResponse format
    
    ALL agents return: {
        "response": "...",
        "metadata": {
            "agent": "agent_name",
            "confidence": 0.9,
            "personality_used": "zen",
            "context_factors": [...],
            "suggested_action": "...",
            "related_transactions": [...]
        }
    }
    """
    
    def __init__(self):
        # Initialize all specialized agents
        self.agents: Dict[AgentType, BaseAgent] = {
            AgentType.SPENDING: SpendingAgent(),
            AgentType.INVESTING: InvestingAgent(),
            AgentType.SAVINGS: SavingsAgent(),
            AgentType.BUDGET: BudgetAgent(),
        }
        
        # Session state storage (in production, use Redis/database)
        self.sessions: Dict[str, Dict] = {}
        
        # Agent routing keywords
        self.routing_map = {
            AgentType.SPENDING: [
                "buy", "purchase", "afford", "should i get", "worth it",
                "spend", "shopping", "expensive", "cost", "price", "item",
                "dining out", "restaurant", "coffee", "impulse", "want"
            ],
            AgentType.INVESTING: [
                "invest", "stock", "portfolio", "401k", "ira", "retirement",
                "index fund", "etf", "dividend", "wealth", "grow money",
                "robinhood", "fidelity", "vanguard", "compound", "returns"
            ],
            AgentType.SAVINGS: [
                "save", "savings", "goal", "emergency fund", "subscription",
                "cancel", "cut back", "reduce", "found money", "extra cash",
                "subscription", "recurring", "membership", "unused"
            ],
            AgentType.BUDGET: [
                "budget", "forecast", "run out", "month end", "overspent",
                "category", "allocation", "on track", "pace", "burn rate",
                "how much left", "can i spend", "dining budget", "grocery budget"
            ]
        }
    
    async def process_query(self, query: AgentQuery) -> AgentResponse:
        """
        Main entry point. Routes query to appropriate agent.
        Maintains session state for context continuity.
        """
        # Determine which agent should handle this
        target_agent = self._route_query(query.query)
        
        # Get or create session state
        session_state = self._get_session_state(query.session_id, query.user_context.user_id)
        
        # Build enhanced query with session context
        enhanced_query = self._build_enhanced_query(
            query.query, 
            session_state,
            query.transaction_context
        )
        
        # Route to specialized agent
        agent = self.agents[target_agent]
        response = await agent.process(
            query=enhanced_query,
            user_context=query.user_context,
            transaction_context=query.transaction_context
        )
        
        # Update session state with this interaction
        self._update_session_state(
            query.session_id, 
            query.user_context.user_id,
            query.query,
            response,
            target_agent.value
        )
        
        # Add routing info to metadata
        response.metadata.agent = target_agent.value
        
        return response
    
    def _route_query(self, query: str) -> AgentType:
        """
        Determine which agent should handle the query.
        Uses keyword matching with confidence scoring.
        """
        query_lower = query.lower()
        scores: Dict[AgentType, int] = {agent: 0 for agent in AgentType if agent != AgentType.GENERAL}
        
        # Score based on keyword matches
        for agent_type, keywords in self.routing_map.items():
            for keyword in keywords:
                if keyword in query_lower:
                    scores[agent_type] += 1
        
        # Determine winner
        max_score = max(scores.values())
        
        if max_score == 0:
            # No clear match - use context clues or default to spending
            return AgentType.SPENDING
        
        # Return agent with highest score
        return max(scores, key=scores.get)
    
    def _get_session_state(self, session_id: Optional[str], user_id: str) -> Dict:
        """Retrieve or initialize session state."""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        
        # Return empty state for new session
        return {
            "history": [],
            "last_agent": None,
            "last_topics": [],
            "user_id": user_id
        }
    
    def _update_session_state(
        self, 
        session_id: Optional[str], 
        user_id: str,
        query: str,
        response: AgentResponse,
        agent_used: str
    ):
        """Update session state with latest interaction."""
        if not session_id:
            return
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "history": [],
                "last_agent": None,
                "last_topics": [],
                "user_id": user_id
            }
        
        session = self.sessions[session_id]
        
        # Add to history (keep last 5)
        session["history"].append({
            "query": query,
            "response": response.response,
            "agent": agent_used
        })
        session["history"] = session["history"][-5:]
        
        # Update last agent
        session["last_agent"] = agent_used
        
        # Extract topics from response
        if response.metadata.suggested_action:
            session["last_topics"].append(response.metadata.suggested_action)
            session["last_topics"] = session["last_topics"][-3:]
    
    def _build_enhanced_query(
        self, 
        query: str, 
        session_state: Dict,
        transaction_context: Optional[List[Dict]] = None
    ) -> str:
        """
        Build enhanced query with session context for better continuity.
        """
        context_parts = [query]
        
        # Add session context if available
        if session_state["history"]:
            recent = session_state["history"][-1]
            context_parts.append(f"\n[Previous context: User previously asked about '{recent['query']}' and you responded about '{recent['response'][:100]}...']")
        
        # Add last agent context for continuity
        if session_state["last_agent"]:
            context_parts.append(f"[Previously discussing with {session_state['last_agent']} agent]")
        
        return "\n".join(context_parts)
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get summary of session for external reference."""
        if session_id in self.sessions:
            return {
                "interaction_count": len(self.sessions[session_id]["history"]),
                "agents_used": list(set(h["agent"] for h in self.sessions[session_id]["history"])),
                "recent_topics": self.sessions[session_id]["last_topics"]
            }
        return None


# Singleton instance for app use
unified_agent = UnifiedAgentRouter()
