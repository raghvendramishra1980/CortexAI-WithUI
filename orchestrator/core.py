"""
CortexOrchestrator - Core business logic layer for CortexAI.

Key guarantees:
- CLI/API layers stay thin (no provider imports there)
- No exceptions bubble up from ask() / compare()
- TokenTracker updates happen here (business layer)
"""

import os
import uuid
from typing import Optional, List, Dict, Any

from api.base_client import BaseAIClient
from models.unified_response import UnifiedResponse, MultiUnifiedResponse, NormalizedError, TokenUsage
from models.user_context import UserContext
from utils.token_tracker import TokenTracker
from utils.cost_calculator import CostCalculator
from utils.logger import get_logger
from orchestrator.multi_orchestrator import MultiModelOrchestrator

logger = get_logger(__name__)


class CortexOrchestrator:
    def __init__(self):
        self._multi_orchestrator = MultiModelOrchestrator()
        self._client_cache: Dict[str, BaseAIClient] = {}

    # ---------- helpers ----------
    def _error_response(
        self,
        *,
        provider: str,
        model: str,
        message: str,
        code: str = "unknown",
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ) -> UnifiedResponse:
        return UnifiedResponse(
            request_id=str(uuid.uuid4()),
            text="",
            provider=provider,
            model=model,
            latency_ms=0,
            token_usage=TokenUsage(0, 0, 0),
            estimated_cost=0.0,
            finish_reason="error",
            error=NormalizedError(
                code=code,
                message=message,
                provider=provider,
                retryable=retryable,
                details=details or {},
            ),
        )

    def _get_client(self, model_type: str, model_name: Optional[str] = None) -> BaseAIClient:
        model_type = (model_type or "").lower().strip()
        cache_key = f"{model_type}:{model_name or 'default'}"
        if cache_key in self._client_cache:
            return self._client_cache[cache_key]

        if model_type == "openai":
            from api.openai_client import OpenAIClient
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            model_name = model_name or os.getenv("DEFAULT_OPENAI_MODEL", "gpt-3.5-turbo")
            client = OpenAIClient(api_key=api_key, model_name=model_name)

        elif model_type == "gemini":
            from api.google_gemini_client import GeminiClient
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_GEMINI_API_KEY not found in environment variables")
            model_name = model_name or os.getenv("DEFAULT_GEMINI_MODEL", "gemini-2.5-flash-lite")
            client = GeminiClient(api_key=api_key, model_name=model_name)

        elif model_type == "deepseek":
            from api.deepseek_client import DeepSeekClient
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
            model_name = model_name or os.getenv("DEFAULT_DEEPSEEK_MODEL", "deepseek-chat")
            client = DeepSeekClient(api_key=api_key, model_name=model_name)

        elif model_type == "grok":
            from api.grok_client import GrokClient
            api_key = os.getenv("GROK_API_KEY")
            if not api_key:
                raise ValueError("GROK_API_KEY not found in environment variables")
            model_name = model_name or os.getenv("DEFAULT_GROK_MODEL", "grok-4-latest")
            client = GrokClient(api_key=api_key, model_name=model_name)

        else:
            raise ValueError(f"Unsupported MODEL_TYPE: {model_type}")

        self._client_cache[cache_key] = client
        logger.info(
            "Initialized client",
            extra={"extra_fields": {"provider": model_type, "model": model_name}},
        )
        return client

    def _build_messages(self, prompt: str, context: Optional[UserContext]) -> List[Dict[str, str]]:
        if context and context.conversation_history:
            msgs = context.get_messages()
            msgs.append({"role": "user", "content": prompt})
            return msgs
        return [{"role": "user", "content": prompt}]

    # ---------- public API ----------
    def ask(
        self,
        prompt: str,
        model_type: str,
        context: Optional[UserContext] = None,
        model_name: Optional[str] = None,
        token_tracker: Optional[TokenTracker] = None,
        **kwargs,
    ) -> UnifiedResponse:
        try:
            client = self._get_client(model_type, model_name)
            messages = self._build_messages(prompt, context)

            resp = client.get_completion(messages=messages, **kwargs)

            # Update token tracker here (business layer)
            if token_tracker:
                token_tracker.update(resp)

            return resp

        except Exception as e:
            logger.exception("ask() failed")
            return self._error_response(
                provider=model_type,
                model=model_name or "default",
                message=str(e),
                code="unknown",
            )

    def compare(
        self,
        prompt: str,
        models_list: List[Dict[str, str]],
        context: Optional[UserContext] = None,
        timeout_s: Optional[float] = None,
        token_tracker: Optional[TokenTracker] = None,
        **kwargs,
    ) -> MultiUnifiedResponse:
        request_group_id = str(uuid.uuid4())
        responses: List[UnifiedResponse] = []

        try:
            messages = self._build_messages(prompt, context)

            clients: List[BaseAIClient] = []
            client_meta: List[Dict[str, str]] = []

            for cfg in models_list:
                provider = (cfg.get("provider") or "").lower().strip()
                model = (cfg.get("model") or "").strip()

                if not provider or not model:
                    responses.append(
                        self._error_response(
                            provider=provider or "unknown",
                            model=model or "unknown",
                            message=f"Invalid model config: {cfg}",
                            code="bad_request",
                        )
                    )
                    continue

                try:
                    c = self._get_client(provider, model)
                    clients.append(c)
                    client_meta.append({"provider": provider, "model": model})
                except Exception as init_err:
                    responses.append(
                        self._error_response(
                            provider=provider,
                            model=model,
                            message=str(init_err),
                            code="auth" if "API_KEY" in str(init_err) else "unknown",
                        )
                    )

            # If we have no valid clients, still return a MultiUnifiedResponse (no exceptions)
            if not clients:
                if token_tracker:
                    for r in responses:
                        token_tracker.update(r)
                return MultiUnifiedResponse.from_responses(request_group_id, prompt, responses)

            # Execute comparisons (parallel inside MultiModelOrchestrator)
            result = self._multi_orchestrator.get_comparisons_sync(
                prompt=prompt,
                clients=clients,
                timeout_s=timeout_s,
                messages=messages,
                **kwargs,
            )

            # Merge init-time failures + runtime results
            responses.extend(result.responses)

            if token_tracker:
                for r in responses:
                    token_tracker.update(r)

            return MultiUnifiedResponse.from_responses(request_group_id, prompt, responses)

        except Exception as e:
            logger.exception("compare() failed")
            responses.append(
                self._error_response(
                    provider="orchestrator",
                    model="compare",
                    message=str(e),
                    code="unknown",
                )
            )
            if token_tracker:
                for r in responses:
                    token_tracker.update(r)
            return MultiUnifiedResponse.from_responses(request_group_id, prompt, responses)

    # --- keep these helpers (your CLI uses them) ---
    def create_token_tracker(self, model_type: str, model_name: Optional[str] = None) -> TokenTracker:
        return TokenTracker(model_type=model_type, model_name=model_name)

    def create_cost_calculator(self, model_type: str, model_name: Optional[str] = None) -> CostCalculator:
        if not model_name:
            if model_type.lower() == "openai":
                model_name = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-3.5-turbo")
            elif model_type.lower() == "gemini":
                model_name = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-2.5-flash-lite")
            elif model_type.lower() == "deepseek":
                model_name = os.getenv("DEFAULT_DEEPSEEK_MODEL", "deepseek-chat")
            elif model_type.lower() == "grok":
                model_name = os.getenv("DEFAULT_GROK_MODEL", "grok-4-latest")
        return CostCalculator(model_type=model_type, model_name=model_name)
