"""
Unified Response Models for AI Provider Abstraction

This module defines the canonical response structure that ALL provider clients
must return. This "locks" the contract and ensures main.py/orchestrator/logging
never access provider-specific SDK response fields.

Design Principles:
- Immutable (frozen=True) to prevent accidental modification
- Provider-agnostic - all providers normalize to this structure
- Error handling built-in - errors are part of the response, not exceptions
- Debug-friendly - raw response available when needed
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass(frozen=True)
class TokenUsage:
    """
    Normalized token usage across all providers.

    All providers must fill these fields. If a provider doesn't report
    token usage, use zeros.
    """
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __post_init__(self):
        """Compute total_tokens if not provided but components exist."""
        if self.total_tokens == 0 and (self.prompt_tokens > 0 or self.completion_tokens > 0):
            # Use object.__setattr__ because dataclass is frozen
            object.__setattr__(self, 'total_tokens', self.prompt_tokens + self.completion_tokens)


@dataclass(frozen=True)
class NormalizedError:
    """
    Normalized error representation across all providers.

    Error Codes (standardized):
    - "timeout": Request timed out
    - "auth": Authentication failed (401, 403, invalid API key)
    - "rate_limit": Rate limit exceeded (429)
    - "bad_request": Invalid request (400, invalid parameters)
    - "provider_error": Provider-side error (500, 502, 503, 504)
    - "unknown": Unclassified error

    All provider-specific errors must be normalized to one of these codes.
    """
    code: str  # One of: timeout, auth, rate_limit, bad_request, provider_error, unknown
    message: str
    provider: str
    retryable: bool = False
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate error code."""
        valid_codes = {"timeout", "auth", "rate_limit", "bad_request", "provider_error", "unknown"}
        if self.code not in valid_codes:
            object.__setattr__(self, 'code', 'unknown')


@dataclass(frozen=True)
class UnifiedResponse:
    """
    The canonical response object that ALL provider clients must return.

    This is the "locked" contract - after implementation, no code outside
    provider adapters should access provider-specific response fields.

    Fields:
    - request_id: Unique identifier for this request (UUID)
    - text: The assistant's response text (empty string if error)
    - provider: Provider name ("openai", "gemini", "deepseek", "grok")
    - model: Actual model used (e.g., "gpt-4", "gemini-1.5-pro")
    - latency_ms: End-to-end request time in milliseconds
    - token_usage: Token counts (prompt, completion, total)
    - estimated_cost: Calculated cost in USD
    - finish_reason: Why generation stopped (normalized)
    - error: Error details if request failed (None if successful)
    - metadata: Additional provider-specific metadata (optional)
    - raw: Full provider response (only if debug/save_full enabled)

    Finish Reasons (normalized):
    - "stop": Natural completion
    - "length": Max tokens reached
    - "tool": Function/tool call triggered
    - "content_filter": Content policy violation
    - "error": Request failed (see error field)
    - None: Unknown/not provided
    """
    request_id: str
    text: str
    provider: str
    model: str
    latency_ms: int
    token_usage: TokenUsage
    estimated_cost: float
    finish_reason: Optional[str] = None
    error: Optional[NormalizedError] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def __post_init__(self):
        """Validate finish_reason."""
        valid_reasons = {"stop", "length", "tool", "content_filter", "error", None}
        if self.finish_reason not in valid_reasons:
            object.__setattr__(self, 'finish_reason', None)

    @property
    def is_success(self) -> bool:
        """Check if the request was successful (no error)."""
        return self.error is None

    @property
    def is_error(self) -> bool:
        """Check if the request failed (has error)."""
        return self.error is not None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for logging/serialization.
        Excludes raw field to avoid large log entries.
        """
        return {
            "request_id": self.request_id,
            "text": self.text if len(self.text) <= 100 else self.text[:100] + "...",
            "provider": self.provider,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "token_usage": {
                "prompt_tokens": self.token_usage.prompt_tokens,
                "completion_tokens": self.token_usage.completion_tokens,
                "total_tokens": self.token_usage.total_tokens,
            },
            "estimated_cost": self.estimated_cost,
            "finish_reason": self.finish_reason,
            "error": {
                "code": self.error.code,
                "message": self.error.message,
                "retryable": self.error.retryable,
            } if self.error else None,
            "timestamp": self.timestamp,
        }
