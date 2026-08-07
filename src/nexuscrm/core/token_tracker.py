"""Senior AI Engineer Token Tracker and Budget Monitor."""

import time
from typing import Dict, Any
from pydantic import BaseModel

from nexuscrm.core.logging import logger


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    latency_seconds: float


class TokenTracker:
    """Tracks token consumption, enforces input/output token limits, and calculates costs."""

    def __init__(
        self,
        max_input_tokens: int = 8000,
        max_output_tokens: int = 2000,
        cost_per_1k_input: float = 0.0005,
        cost_per_1k_output: float = 0.0015,
        call_delay_seconds: float = 2.0,
    ):
        self.max_input_tokens = max_input_tokens
        self.max_output_tokens = max_output_tokens
        self.cost_per_1k_input = cost_per_1k_input
        self.cost_per_1k_output = cost_per_1k_output
        self.call_delay_seconds = call_delay_seconds
        self.last_call_time: float = 0.0
        self.cumulative_tokens: int = 0
        self.cumulative_cost: float = 0.0

    def estimate_token_count(self, text: str) -> int:
        """Estimate token count based on standard ~4 characters per token heuristic."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def validate_limits(self, prompt_text: str) -> bool:
        """Validate if input token count is within allowed max bounds."""
        estimated_input = self.estimate_token_count(prompt_text)
        if estimated_input > self.max_input_tokens:
            logger.warning(f"Token Budget Exceeded: Input token count ({estimated_input}) exceeds max limit ({self.max_input_tokens}).")
            return False
        return True

    def enforce_rate_delay(self):
        """Enforce standard polite 2-second delay between consecutive LLM API invocations."""
        now = time.time()
        elapsed = now - self.last_call_time
        if self.last_call_time > 0 and elapsed < self.call_delay_seconds:
            sleep_time = self.call_delay_seconds - elapsed
            logger.info(f"API Rate Throttler: Enforcing {sleep_time:.2f}s polite delay between LLM calls...")
            time.sleep(sleep_time)
        self.last_call_time = time.time()

    def record_usage(self, prompt_text: str, response_text: str, latency: float = 0.0) -> TokenUsage:
        """Record token usage, calculate cost, and update global budget tracking."""
        in_tokens = self.estimate_token_count(prompt_text)
        out_tokens = self.estimate_token_count(response_text)
        total_tokens = in_tokens + out_tokens

        cost = (in_tokens / 1000.0 * self.cost_per_1k_input) + (out_tokens / 1000.0 * self.cost_per_1k_output)

        self.cumulative_tokens += total_tokens
        self.cumulative_cost += cost

        logger.info(
            f"TokenUsage: Input={in_tokens}, Output={out_tokens}, Total={total_tokens}, "
            f"Cost=${cost:.6f}, CumulativeCost=${self.cumulative_cost:.4f}"
        )

        return TokenUsage(
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=round(cost, 6),
            latency_seconds=round(latency, 3),
        )


token_tracker = TokenTracker()
