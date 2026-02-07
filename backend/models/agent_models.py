from pydantic import BaseModel
from typing import Literal, Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class FinancialPersonality(str, Enum):
    ZEN = "zen"
    TOUGH_LOVE = "tough_love"
    TO_THE_POINT = "to_the_point"
    NO_BS = "no_bs"
    SUPPORTIVE = "supportive"


class AgentType(str, Enum):
    SPENDING = "spending"
    INVESTING = "investing"
    SAVINGS = "savings"
    BUDGET = "budget"
    GENERAL = "general"


class UserContext(BaseModel):
    user_id: str
    financial_personality: FinancialPersonality = FinancialPersonality.SUPPORTIVE
    payday_day: int = 15  # Day of month (1-31)
    monthly_income: float = 5000.0
    current_balance: float = 2500.0
    monthly_budget: float = 4000.0
    timezone: str = "America/New_York"
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "financial_personality": "supportive",
                "payday_day": 15,
                "monthly_income": 5000.0,
                "current_balance": 2500.0,
                "monthly_budget": 4000.0,
                "timezone": "America/New_York"
            }
        }


class AgentQuery(BaseModel):
    query: str
    user_context: UserContext
    session_id: Optional[str] = None
    transaction_context: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Should I buy this $200 jacket?",
                "user_context": {
                    "user_id": "user_123",
                    "financial_personality": "tough_love",
                    "payday_day": 15,
                    "monthly_income": 5000.0,
                    "current_balance": 1200.0,
                    "monthly_budget": 4000.0,
                    "timezone": "America/New_York"
                },
                "session_id": "session_abc_123",
                "transaction_context": [
                    {
                        "id": "txn_001",
                        "amount": 45.67,
                        "category": "food",
                        "merchant": "Chipotle",
                        "date": "2024-02-01T12:00:00Z",
                        "type": "debit"
                    }
                ]
            }
        }


class AgentMetadata(BaseModel):
    agent: str
    confidence: float
    personality_used: str
    context_factors: List[str]
    suggested_action: Optional[str] = None
    related_transactions: Optional[List[str]] = None


class AgentResponse(BaseModel):
    """
    STANDARDIZED OUTPUT FORMAT - ALL AGENTS MUST RETURN THIS STRUCTURE
    """
    response: str
    metadata: AgentMetadata
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Based on your current balance of $1,200 and the fact that you're 10 days from payday, that $200 jacket would take 16% of your remaining funds. I'd recommend waiting until after payday.",
                "metadata": {
                    "agent": "spending",
                    "confidence": 0.92,
                    "personality_used": "tough_love",
                    "context_factors": [
                        "10 days until payday",
                        "balance below monthly average",
                        "discretionary purchase"
                    ],
                    "suggested_action": "delay_purchase",
                    "related_transactions": ["txn_001", "txn_002"]
                }
            }
        }


class PersonalityPrompt(BaseModel):
    name: str
    description: str
    system_prompt_addition: str


class ContextAnalysis(BaseModel):
    days_until_payday: int
    days_since_payday: int
    month_progress_percent: float
    budget_remaining_percent: float
    balance_status: Literal["critical", "low", "normal", "healthy"]
    spending_velocity: Literal["high", "normal", "low"]
    time_context: Literal["early_month", "mid_month", "pre_payday", "post_payday"]
