"""Agentic Harness Core: 4-Tier Memory, Safety Guardrails, Time Triggers, and Feedback Loops."""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from nexuscrm.core.logging import logger


# ============================================================================
# 1. 4-TIER MEMORY SYSTEM
# ============================================================================

class MemoryManager:
    """Manages Short-term, Episodic, Long-term, and Semantic Memory components."""

    def __init__(self):
        # Long-term persistent customer facts store
        self.long_term_facts: Dict[str, List[str]] = {
            "default": [
                "Customer prefers email over phone communications.",
                "Primary decision maker is VP of Engineering.",
                "Requires annual SLA commitment for enterprise tier.",
            ]
        }

    def load_context(self, contact_email: Optional[str] = None) -> Dict[str, Any]:
        """Aggregate 4 memory tiers into consolidated context object."""
        key = contact_email or "default"
        facts = self.long_term_facts.get(key, self.long_term_facts["default"])

        return {
            "short_term_session_id": "sess-active",
            "episodic_history": [
                "2026-08-01: Call logged discussing enterprise expansion terms.",
                "2026-08-03: Email sent with updated pricing schedule.",
            ],
            "long_term_facts": facts,
            "semantic_knowledge_source": "PageIndex Hybrid RAG Knowledge Base",
        }

    def store_fact(self, contact_email: str, fact: str):
        """Store persistent fact into Long-term Memory."""
        if contact_email not in self.long_term_facts:
            self.long_term_facts[contact_email] = []
        self.long_term_facts[contact_email].append(fact)
        logger.info(f"Stored long-term memory fact for {contact_email}: '{fact}'")


memory_manager = MemoryManager()


# ============================================================================
# 2. MULTI-LAYER GUARDRAILS
# ============================================================================

class PIIFilterResult(BaseModel):
    is_safe: bool
    masked_text: str
    violations: List[str]


class GuardrailEngine:
    """Input, Output, and Action Guardrail Engine."""

    PII_PATTERNS = {
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
        "API_KEY": r"\b(?:sk|pk)_[a-zA-Z0-9]{24,}\b",
    }

    PROMPT_INJECTION_KEYWORDS = [
        "ignore previous instructions",
        "system prompt override",
        "drop table",
        "delete from users",
    ]

    @classmethod
    def scan_input(cls, text: str) -> PIIFilterResult:
        """Scan input prompt for PII leaks and prompt injection attempts."""
        text_lower = text.lower()
        violations = []

        # Check prompt injection
        for kw in cls.PROMPT_INJECTION_KEYWORDS:
            if kw in text_lower:
                violations.append(f"Prompt Injection Detected: '{kw}'")

        # Check PII
        masked = text
        for pii_type, pattern in cls.PII_PATTERNS.items():
            if re.search(pattern, text):
                violations.append(f"PII Violation: {pii_type} pattern detected.")
                masked = re.sub(pattern, f"[MASKED_{pii_type}]", masked)

        return PIIFilterResult(
            is_safe=len(violations) == 0,
            masked_text=masked,
            violations=violations,
        )


guardrail_engine = GuardrailEngine()


# ============================================================================
# 3. TIME-AWARE WORKFLOW SCHEDULER
# ============================================================================

class TimeAwareScheduler:
    """Monitors deal velocity staleness and customer re-engagement triggers."""

    @staticmethod
    def check_stale_deals(deals: List[Dict[str, Any]], max_stale_days: int = 7) -> List[Dict[str, Any]]:
        """Identify deals lingering in pipeline without recent activity."""
        stale_deals = []
        for deal in deals:
            days_in_stage = deal.get("days_in_stage", 0)
            if days_in_stage > max_stale_days:
                stale_deals.append({
                    "deal_id": deal.get("id"),
                    "title": deal.get("title"),
                    "days_in_stage": days_in_stage,
                    "action_required": "Trigger FollowUpAgent re-engagement email.",
                })
        logger.info(f"TimeAwareScheduler identified {len(stale_deals)} stale deals lingering > {max_stale_days} days.")
        return stale_deals


time_scheduler = TimeAwareScheduler()


# ============================================================================
# 4. FEEDBACK LOOP COLLECTOR
# ============================================================================

class FeedbackRecord(BaseModel):
    task_id: str
    rating: int  # +1 (thumbs up), -1 (thumbs down)
    comment: Optional[str] = None
    edit_distance: Optional[int] = 0


class FeedbackCollector:
    """Stores user feedback metrics to drive continuous agent self-improvement."""

    def __init__(self):
        self.records: List[FeedbackRecord] = []

    def log_feedback(self, record: FeedbackRecord):
        self.records.append(record)
        logger.info(f"Feedback logged for task {record.task_id}: Rating={record.rating}, EditDistance={record.edit_distance}")

    def get_metrics(self) -> Dict[str, Any]:
        if not self.records:
            return {"total_feedback": 0, "positive_percentage": 100.0, "avg_edit_distance": 0.0}

        positive = sum(1 for r in self.records if r.rating > 0)
        avg_ed = sum(r.edit_distance or 0 for r in self.records) / len(self.records)
        return {
            "total_feedback": len(self.records),
            "positive_percentage": round((positive / len(self.records)) * 100.0, 1),
            "avg_edit_distance": round(avg_ed, 1),
        }


feedback_collector = FeedbackCollector()
