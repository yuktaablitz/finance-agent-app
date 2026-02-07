# router.py

import asyncio
from typing import Dict, Optional

from agents.unified_agent import unified_agent
from models.agent_models import AgentQuery, UserContext, FinancialPersonality


class Router:

    def __init__(self):
        # Backward-compatible Router.
        # The authoritative routing logic now lives in agents/unified_agent.py.
        pass

    def classify_intent(self, message: str) -> str:
        """
        Simple starter intent classification.
        Replace later with LLM classifier.
        """

        # Legacy API compatibility only. The unified agent router decides this now.
        return "general"

    def dispatch(self, message: str, context: dict):
        """Legacy dispatch() wrapper that routes to the new unified agent.

        Returns: (agent_used, response_dict)
        - agent_used: str
        - response_dict: standardized {"response": ..., "metadata": {...}}
        """

        user_id = str(context.get("user_id", "unknown_user"))
        session_id = context.get("session_id")

        # Legacy compatibility: map any old "tone" string to the new enum.
        financial_personality = self._map_legacy_tone_to_personality(context.get("tone"))
        
        user_ctx = UserContext(
            user_id=user_id,
            financial_personality=financial_personality,
        )

        query = AgentQuery(
            query=message,
            user_context=user_ctx,
            session_id=session_id,
            transaction_context=context.get("transaction_context"),
        )

        agent_response = self._run_async(unified_agent.process_query(query))

        # Keep return signature similar to old router: (agent_used, response)
        return agent_response.metadata.agent, agent_response.model_dump()

    def _map_legacy_tone_to_personality(self, tone: Optional[str]) -> FinancialPersonality:
        if not tone:
            return FinancialPersonality.SUPPORTIVE

        t = str(tone).strip().lower()
        mapping: Dict[str, FinancialPersonality] = {
            "zen": FinancialPersonality.ZEN,
            "zen_coach": FinancialPersonality.ZEN,
            "tough": FinancialPersonality.TOUGH_LOVE,
            "tough_love": FinancialPersonality.TOUGH_LOVE,
            "support": FinancialPersonality.SUPPORTIVE,
            "to_the_point": FinancialPersonality.TO_THE_POINT,
            "no_bs": FinancialPersonality.NO_BS,
        }

        return mapping.get(t, FinancialPersonality.SUPPORTIVE)

    def _run_async(self, coro):
        """Run an async coroutine from sync context safely."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If we're already in an event loop, create a new task and wait.
            # This path is rarely used in our current FastAPI setup, but keeps compatibility.
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            return future.result()

        return asyncio.run(coro)
