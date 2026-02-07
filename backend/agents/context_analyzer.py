"""
Context Analyzer
Analyzes timing context (payday proximity, month-end, spending patterns)
for dynamic tone adjustment
"""

from datetime import datetime, timedelta
from typing import Dict, List
from models.agent_models import UserContext, ContextAnalysis


class ContextAnalyzer:
    def __init__(self, user_context: UserContext):
        self.user_context = user_context
        self.now = datetime.now()
        self.current_day = self.now.day
        self.days_in_month = self._get_days_in_month()
    
    def _get_days_in_month(self) -> int:
        """Get number of days in current month."""
        if self.now.month == 12:
            next_month = self.now.replace(year=self.now.year + 1, month=1, day=1)
        else:
            next_month = self.now.replace(month=self.now.month + 1, day=1)
        last_day = next_month - timedelta(days=1)
        return last_day.day
    
    def analyze(self) -> ContextAnalysis:
        """Analyze current financial and temporal context."""
        days_until = self._days_until_payday()
        days_since = self._days_since_payday()
        
        month_progress = (self.current_day / self.days_in_month) * 100
        
        budget_spent = self.user_context.monthly_budget - self.user_context.current_balance
        budget_remaining_pct = ((self.user_context.monthly_budget - budget_spent) / self.user_context.monthly_budget) * 100 if self.user_context.monthly_budget > 0 else 0
        
        balance_status = self._calculate_balance_status()
        spending_velocity = self._calculate_spending_velocity()
        time_context = self._determine_time_context(days_until, days_since)
        
        return ContextAnalysis(
            days_until_payday=days_until,
            days_since_payday=days_since,
            month_progress_percent=round(month_progress, 1),
            budget_remaining_percent=round(budget_remaining_pct, 1),
            balance_status=balance_status,
            spending_velocity=spending_velocity,
            time_context=time_context
        )
    
    def _days_until_payday(self) -> int:
        """Calculate days until next payday."""
        payday = self.user_context.payday_day
        if self.current_day <= payday:
            return payday - self.current_day
        else:
            return self.days_in_month - self.current_day + payday
    
    def _days_since_payday(self) -> int:
        """Calculate days since last payday."""
        payday = self.user_context.payday_day
        if self.current_day >= payday:
            return self.current_day - payday
        else:
            return self.days_in_month - payday + self.current_day
    
    def _calculate_balance_status(self) -> str:
        """Determine if balance is critical, low, normal, or healthy."""
        daily_budget = self.user_context.monthly_budget / 30
        days_until = self._days_until_payday()
        minimum_needed = daily_budget * days_until
        
        if self.user_context.current_balance < minimum_needed * 0.5:
            return "critical"
        elif self.user_context.current_balance < minimum_needed:
            return "low"
        elif self.user_context.current_balance < self.user_context.monthly_income * 0.3:
            return "normal"
        else:
            return "healthy"
    
    def _calculate_spending_velocity(self) -> str:
        """Determine if spending is high, normal, or low based on month progress vs budget used."""
        month_progress = self.current_day / self.days_in_month
        budget_used = (self.user_context.monthly_budget - self.user_context.current_balance) / self.user_context.monthly_budget if self.user_context.monthly_budget > 0 else 0
        
        if budget_used > month_progress * 1.3:
            return "high"
        elif budget_used < month_progress * 0.7:
            return "low"
        else:
            return "normal"
    
    def _determine_time_context(self, days_until: int, days_since: int) -> str:
        """Determine current time phase of month."""
        if days_until <= 3:
            return "pre_payday"
        elif days_since <= 3:
            return "post_payday"
        elif self.current_day <= 10:
            return "early_month"
        else:
            return "mid_month"
    
    def get_context_prompt_addition(self) -> str:
        """Generate context-aware prompt addition based on timing."""
        analysis = self.analyze()
        factors = []
        
        # Time-based factors
        if analysis.days_until_payday <= 3:
            factors.append(f"CRITICAL: Only {analysis.days_until_payday} days until payday - emphasize caution")
        elif analysis.days_until_payday <= 7:
            factors.append(f"{analysis.days_until_payday} days until payday - suggest restraint")
        elif analysis.days_since_payday <= 3:
            factors.append(f"Just got paid {analysis.days_since_payday} days ago - good time for planned purchases")
        
        if analysis.time_context == "early_month":
            factors.append("Early in month - can be more flexible")
        elif analysis.time_context == "mid_month":
            factors.append("Mid-month - stay on track")
        
        # Balance-based factors
        if analysis.balance_status == "critical":
            factors.append("CRITICAL: Balance dangerously low - strongly discourage non-essential spending")
        elif analysis.balance_status == "low":
            factors.append("Balance is low - recommend caution")
        elif analysis.balance_status == "healthy":
            factors.append("Balance is healthy - can be more flexible")
        
        # Spending velocity
        if analysis.spending_velocity == "high":
            factors.append("Spending faster than planned - advise slowing down")
        elif analysis.spending_velocity == "low":
            factors.append("Under budget - good position")
        
        return "\n".join(factors) if factors else "Context: Normal financial period"
    
    def get_context_factors(self) -> List[str]:
        """Get list of current context factors for metadata."""
        analysis = self.analyze()
        factors = []
        
        if analysis.days_until_payday <= 7:
            factors.append(f"{analysis.days_until_payday} days until payday")
        if analysis.balance_status in ["critical", "low"]:
            factors.append(f"{analysis.balance_status} balance")
        if analysis.spending_velocity == "high":
            factors.append("high spending velocity")
        if analysis.budget_remaining_percent < 20:
            factors.append("low budget remaining")
        
        return factors if factors else ["normal financial period"]
