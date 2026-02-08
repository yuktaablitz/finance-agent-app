# personality/tone_engine.py

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple


class ToneEngine:
    """
    Personality engine with three tones and payday effect detection.
    
    Tones:
    - zen_coach: "Let's think about your long-term peace of mind..."
    - tough_love: "You said you wanted to save. Skip the bag."
    - supportive: "I know it's tempting, but you're doing great staying on track!"
    
    Payday Effect:
    - Detects overspending patterns after payday
    - Provides proactive warnings and suggestions
    """

    TONES = {
        "zen_coach": "Let's think about your long-term peace of mind...",
        "tough_love": "You said you wanted to save. Skip the bag.",
        "supportive": "I know it's tempting, but you're doing great staying on track!",
        "to_the_point": "Here are the facts.",
        "no_bs": "Let's cut to the chase."
    }

    def __init__(self):
        self.default_tone = "supportive"
        self.payday_detection_window = 3  # Days after payday to monitor

    def determine_tone(
        self,
        user_choice: Optional[str],
        memory_data: Dict,
        message: Optional[str] = None,
        current_date: Optional[datetime] = None
    ) -> str:
        """
        Determine the appropriate tone.
        
        Priority:
        1. Explicit user choice
        2. Learned preference from memory
        3. Context-based selection (default: supportive)
        """
        if current_date is None:
            current_date = datetime.now()

        # Normalize user choice
        if user_choice:
            normalized = self._normalize_tone(user_choice)
            if normalized:
                return normalized

        # Check memory for preferred tone
        if memory_data and "preferred_tone" in memory_data:
            preferred = self._normalize_tone(memory_data["preferred_tone"])
            if preferred:
                return preferred

        # Default to supportive
        return self.default_tone

    def _normalize_tone(self, tone: str) -> Optional[str]:
        """
        Normalize tone input to one of the five valid tones.
        """
        if not tone:
            return None
        
        tone_lower = tone.lower().strip()
        
        # Direct matches
        if tone_lower in ["zen_coach", "zen", "coach"]:
            return "zen_coach"
        elif tone_lower in ["tough_love", "tough", "strict", "firm"]:
            return "tough_love"
        elif tone_lower in ["supportive", "support", "encouraging", "kind"]:
            return "supportive"
        elif tone_lower in ["to_the_point", "to the point", "brief", "concise"]:
            return "to_the_point"
        elif tone_lower in ["no_bs", "no bs", "nobs", "direct", "blunt"]:
            return "no_bs"
        
        return None

    def detect_payday_effect(
        self,
        memory_data: Dict,
        current_date: Optional[datetime] = None
    ) -> Optional[Dict]:
        """
        Detect payday effect - overspending patterns after payday.
        
        Returns:
            Dict with payday effect info if detected, None otherwise
            {
                "is_payday_period": bool,
                "days_since_payday": int,
                "average_overspend": float,
                "warning_message": str,
                "suggestion": str
            }
        """
        if current_date is None:
            current_date = datetime.now()

        if not memory_data:
            return None

        # Get payday info from memory
        payday_info = memory_data.get("payday_info", {})
        if not payday_info:
            return None

        # Get last payday date
        last_payday_str = payday_info.get("last_payday")
        if not last_payday_str:
            return None

        try:
            last_payday = datetime.fromisoformat(last_payday_str)
        except (ValueError, TypeError):
            return None

        # Calculate days since payday
        days_since = (current_date - last_payday).days

        # Check if we're in the payday detection window (0-3 days after payday)
        if days_since < 0 or days_since > self.payday_detection_window:
            return None

        # Get spending patterns
        spending_patterns = payday_info.get("spending_patterns", {})
        average_overspend = spending_patterns.get("average_overspend_after_payday", 0)
        
        # Get spending history for this payday period
        current_spending = self._get_current_payday_spending(memory_data, last_payday, current_date)

        return {
            "is_payday_period": True,
            "days_since_payday": days_since,
            "average_overspend": average_overspend,
            "current_spending": current_spending,
            "warning_message": self._generate_payday_warning(average_overspend, days_since),
            "suggestion": self._generate_payday_suggestion(average_overspend, current_spending)
        }

    def _get_current_payday_spending(
        self,
        memory_data: Dict,
        payday_date: datetime,
        current_date: datetime
    ) -> float:
        """
        Calculate current spending in the payday period.
        """
        spending_history = memory_data.get("spending_history", [])
        if not spending_history:
            return 0.0

        total = 0.0
        for entry in spending_history:
            if isinstance(entry, dict):
                entry_date_str = entry.get("date")
                if entry_date_str:
                    try:
                        entry_date = datetime.fromisoformat(entry_date_str)
                        if payday_date <= entry_date <= current_date:
                            amount = entry.get("amount", 0)
                            if isinstance(amount, (int, float)):
                                total += float(amount)
                    except (ValueError, TypeError):
                        continue

        return total

    def _generate_payday_warning(self, average_overspend: float, days_since: int) -> str:
        """
        Generate warning message about payday spending pattern.
        """
        if average_overspend > 0:
            return f"Heads up: you typically overspend by ${average_overspend:.2f} in the 3 days after getting paid"
        return "You just got paid—this is when you typically spend more."

    def _generate_payday_suggestion(self, average_overspend: float, current_spending: float) -> str:
        """
        Generate proactive suggestion for payday period.
        """
        if average_overspend > 0:
            suggested_amount = min(average_overspend * 0.5, 200)  # Suggest saving half, max $200
            return f"You just got paid—want to transfer ${suggested_amount:.0f} to savings first?"
        return "You just got paid—want to transfer $200 to savings first?"

    def update_payday_info(
        self,
        memory_data: Dict,
        payday_date: datetime,
        spending_amount: float
    ) -> Dict:
        """
        Update payday information in memory.
        Tracks spending patterns after payday.
        """
        if "payday_info" not in memory_data:
            memory_data["payday_info"] = {
                "last_payday": payday_date.isoformat(),
                "spending_patterns": {
                    "payday_periods": [],
                    "average_overspend_after_payday": 0
                }
            }

        payday_info = memory_data["payday_info"]
        payday_info["last_payday"] = payday_date.isoformat()

        # Track spending in payday period
        if "spending_history" not in memory_data:
            memory_data["spending_history"] = []

        memory_data["spending_history"].append({
            "date": datetime.now().isoformat(),
            "amount": spending_amount,
            "type": "payday_period"
        })

        # Calculate average overspend after payday
        self._calculate_payday_patterns(memory_data)

        return memory_data

    def _calculate_payday_patterns(self, memory_data: Dict):
        """
        Calculate average overspending after payday from historical data.
        """
        payday_info = memory_data.get("payday_info", {})
        spending_patterns = payday_info.get("spending_patterns", {})
        
        spending_history = memory_data.get("spending_history", [])
        if not spending_history:
            return

        # Group spending by payday periods
        payday_periods = []
        current_period = []
        last_payday = None

        for entry in sorted(spending_history, key=lambda x: x.get("date", "")):
            if not isinstance(entry, dict):
                continue

            entry_date_str = entry.get("date")
            if not entry_date_str:
                continue

            try:
                entry_date = datetime.fromisoformat(entry_date_str)
            except (ValueError, TypeError):
                continue

            # Check if this is a new payday period
            if last_payday is None or (entry_date - last_payday).days > self.payday_detection_window:
                if current_period:
                    payday_periods.append(current_period)
                current_period = []
                last_payday = entry_date

            if entry.get("type") == "payday_period":
                current_period.append(entry.get("amount", 0))

        if current_period:
            payday_periods.append(current_period)

        # Calculate average overspend (assuming normal spending is baseline)
        if payday_periods:
            period_totals = [sum(period) for period in payday_periods if period]
            if period_totals:
                # Simple heuristic: if spending > $100 in 3 days after payday, consider it overspend
                baseline = 100
                overspends = [max(0, total - baseline) for total in period_totals]
                average_overspend = sum(overspends) / len(overspends) if overspends else 0
                
                spending_patterns["average_overspend_after_payday"] = round(average_overspend, 2)
                spending_patterns["payday_periods"] = payday_periods

        payday_info["spending_patterns"] = spending_patterns

    def get_tone_description(self, tone: str) -> str:
        """
        Get the description/phrase for a tone.
        """
        return self.TONES.get(tone, self.TONES[self.default_tone])

    def get_date_context(self, current_date: Optional[datetime] = None) -> Dict:
        """
        Get date context information.
        """
        if current_date is None:
            current_date = datetime.now()

        return {
            "date": current_date.isoformat(),
            "day_of_month": current_date.day,
            "day_name": current_date.strftime("%A"),
            "month": current_date.month,
            "month_name": current_date.strftime("%B"),
        }


# Backward compatibility function
def determine_tone(user_choice: Optional[str], memory_data: Dict, message: Optional[str] = None) -> str:
    """
    Backward compatible function for existing code.
    """
    engine = ToneEngine()
    return engine.determine_tone(user_choice, memory_data, message)
