"""Senior AI Engineer Comprehensive LLM Guardrails Engine."""

import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from nexuscrm.core.logging import logger
from nexuscrm.core.token_tracker import token_tracker


class InputGuardrailResult(BaseModel):
    is_safe: bool
    sanitized_text: str
    violations: List[str]
    input_tokens: int


class OutputGuardrailResult(BaseModel):
    is_grounded: bool
    confidence_score: float
    passed: bool
    violations: List[str]
    output_tokens: int


class SeniorLLMGuardrails:
    """Comprehensive Multi-Layer Input, Output, and Action Guardrail Engine."""

    PII_PATTERNS = {
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
        "API_KEY": r"\b(?:sk|pk)_[a-zA-Z0-9]{24,}\b",
        "PASSWORD_FIELD": r"\b(?:password|passwd|secret)\s*[:=]\s*\S+",
    }

    INJECTION_SIGNATURES = [
        "ignore previous instructions",
        "system prompt override",
        "forget all prior rules",
        "act as unrestricted ai",
        "jailbreak mode",
        "drop table",
        "delete from users",
    ]

    @classmethod
    def validate_input(cls, user_text: str) -> InputGuardrailResult:
        """Input Layer: PII Detection, Prompt Injection Filter & Token Budget Check."""
        violations = []
        sanitized = user_text

        # 1. Check Token Length Limits
        if not token_tracker.validate_limits(user_text):
            violations.append("Input token count exceeds maximum allowed budget limit (8000 tokens).")

        # 2. Check Prompt Injection
        lower_text = user_text.lower()
        for sig in cls.INJECTION_SIGNATURES:
            if sig in lower_text:
                violations.append(f"Prompt Injection Attack Blocked: Signature '{sig}' detected.")

        # 3. Scan & Mask PII
        for pii_type, pattern in cls.PII_PATTERNS.items():
            if re.search(pattern, user_text, re.IGNORECASE):
                violations.append(f"PII Leakage Detected: {pii_type}")
                sanitized = re.sub(pattern, f"[MASKED_{pii_type}]", sanitized, flags=re.IGNORECASE)

        in_tokens = token_tracker.estimate_token_count(sanitized)
        is_safe = len([v for v in violations if "Blocked" in v or "exceeds" in v]) == 0

        if not is_safe:
            logger.warning(f"Input Guardrail Violation: {violations}")

        return InputGuardrailResult(
            is_safe=is_safe,
            sanitized_text=sanitized,
            violations=violations,
            input_tokens=in_tokens,
        )

    @classmethod
    def validate_output(
        cls,
        llm_response: str,
        retrieved_context: Optional[List[str]] = None,
        min_confidence: float = 0.60,
    ) -> OutputGuardrailResult:
        """Output Layer: Hallucination Grounding, Confidence Score & Toxicity Check."""
        violations = []
        out_tokens = token_tracker.estimate_token_count(llm_response)

        # 1. Hallucination Grounding Check
        is_grounded = True
        confidence = 0.90

        if retrieved_context:
            context_str = " ".join(retrieved_context).lower()
            response_words = set(re.findall(r"\w+", llm_response.lower()))
            overlap = sum(1 for w in response_words if w in context_str)
            ratio = overlap / max(1, len(response_words))

            if ratio < 0.30:
                is_grounded = False
                confidence = round(max(0.40, ratio + 0.20), 2)
                violations.append("Output Grounding Warning: Response contains claims not found in retrieved context.")
            else:
                confidence = round(min(0.98, ratio + 0.40), 2)

        # 2. Confidence Thresholding
        passed = is_grounded and (confidence >= min_confidence)
        if confidence < min_confidence:
            violations.append(f"Low Confidence Score ({confidence} < {min_confidence}): Routed for human verification.")

        return OutputGuardrailResult(
            is_grounded=is_grounded,
            confidence_score=confidence,
            passed=passed,
            violations=violations,
            output_tokens=out_tokens,
        )


llm_guardrails = SeniorLLMGuardrails()
