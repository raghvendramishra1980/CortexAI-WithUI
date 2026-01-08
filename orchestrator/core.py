"""
CortexOrchestrator - Core business logic layer for CortexAI.

Separates orchestration logic from CLI/API interfaces to enable:
- CLI integration (main.py)
- FastAPI REST endpoints (future)
- Python SDK (future)
- gRPC/WebSocket services (future)
"""

import os
from typing import Optional, List, Dict, Any
from api.base_client import BaseAIClient
from models.unified_response import UnifiedResponse
from models.multi_unified_response import MultiUnifiedResponse
from models.user_context import UserContext
from utils.token_tracker import TokenTracker
from utils.cost_calculator import CostCalculator
from utils.logger import get_logger
from orchestrator.multi_orchestrator import MultiModelOrchestrator

logger = get_logger(__name__)


class CortexOrchestrator:
    """
    Stateless orchestrator for AI model interactions.

    Coordinates client initialization, request routing, token tracking,
    and cost calculation without maintaining session state. All session
    data is passed via UserContext for true statelessness.
    """

    def __init__(self):
        """Initialize the orchestrator."""
        self._multi_orchestrator = MultiModelOrchestrator()
        self._client_cache: Dict[str, BaseAIClient] = {}

    def _get_client(self, model_type: str, model_name: Optional[str] = None) -> BaseAIClient:
        """
        Get or create a client for the specified model type.

        Args:
            model_type: Provider type ('openai', 'gemini', 'deepseek', 'grok')
            model_name: Optional specific model name

        Returns:
            Initialized BaseAIClient instance

        Raises:
            ValueError: If model_type is unsupported or API key is missing
        """
        # Create cache key
        cache_key = f"{model_type}:{model_name or 'default'}"

        # Return cached client if available
        if cache_key in self._client_cache:
            return self._client_cache[cache_key]

        # Initialize new client
        model_type = model_type.lower()

        if model_type == 'openai':
            from api.openai_client import OpenAIClient
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            model_name = model_name or os.getenv('DEFAULT_OPENAI_MODEL', 'gpt-3.5-turbo')
            client = OpenAIClient(api_key=api_key, model_name=model_name)

        elif model_type == 'gemini':
            from api.google_gemini_client import GeminiClient
            api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_GEMINI_API_KEY not found in environment variables")
            model_name = model_name or os.getenv('DEFAULT_GEMINI_MODEL', 'gemini-2.5-flash-lite')
            client = GeminiClient(api_key=api_key, model_name=model_name)

        elif model_type == 'deepseek':
            from api.deepseek_client import DeepSeekClient
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
            model_name = model_name or os.getenv('DEFAULT_DEEPSEEK_MODEL', 'deepseek-chat')
            client = DeepSeekClient(api_key=api_key, model_name=model_name)

        elif model_type == 'grok':
            from api.grok_client import GrokClient
            api_key = os.getenv('GROK_API_KEY')
            if not api_key:
                raise ValueError("GROK_API_KEY not found in environment variables")
            model_name = model_name or os.getenv('DEFAULT_GROK_MODEL', 'grok-4-latest')
            client = GrokClient(api_key=api_key, model_name=model_name)

        else:
            raise ValueError(
                f"Unsupported MODEL_TYPE: {model_type}. "
                f"Must be 'openai', 'gemini', 'deepseek', or 'grok'"
            )

        logger.info(
            f"Initialized {model_type} client",
            extra={"extra_fields": {"model": model_name, "model_type": model_type}}
        )

        # Cache and return
        self._client_cache[cache_key] = client
        return client

    def ask(
        self,
        prompt: str,
        model_type: str,
        context: Optional[UserContext] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> UnifiedResponse:
        """
        Execute a single-model request.

        This is the primary method for standard AI interactions. It:
        1. Initializes the appropriate client
        2. Calls get_completion() with conversation context
        3. Returns UnifiedResponse with token/cost data

        Args:
            prompt: User prompt/query
            model_type: Provider type ('openai', 'gemini', 'deepseek', 'grok')
            context: Optional UserContext with conversation history
            model_name: Optional specific model name
            **kwargs: Additional parameters passed to get_completion()

        Returns:
            UnifiedResponse with result, tokens, cost, and metadata

        Example:
            >>> orchestrator = CortexOrchestrator()
            >>> context = UserContext()
            >>> response = orchestrator.ask(
            ...     prompt="What is Python?",
            ...     model_type="openai",
            ...     context=context
            ... )
            >>> print(response.text)
        """
        logger.debug(
            f"Processing ask request",
            extra={"extra_fields": {
                "model_type": model_type,
                "model_name": model_name,
                "prompt_length": len(prompt),
                "has_context": context is not None
            }}
        )

        # Get client
        client = self._get_client(model_type, model_name)

        # Build messages from context
        if context and context.conversation_history:
            # Use full conversation history
            messages = context.get_messages()
            # Add current prompt
            messages.append({"role": "user", "content": prompt})
        else:
            # No context - single message
            messages = [{"role": "user", "content": prompt}]

        # Call client
        response = client.get_completion(messages=messages, **kwargs)

        logger.info(
            "Ask request completed",
            extra={"extra_fields": {
                "request_id": response.request_id,
                "provider": response.provider,
                "model": response.model,
                "is_error": response.is_error,
                "tokens": response.token_usage.total_tokens,
                "cost": response.estimated_cost
            }}
        )

        return response

    def compare(
        self,
        prompt: str,
        models_list: List[Dict[str, str]],
        context: Optional[UserContext] = None,
        timeout_s: Optional[float] = None,
        **kwargs
    ) -> MultiUnifiedResponse:
        """
        Execute a multi-model comparison request.

        Sends the same prompt to multiple models in parallel and returns
        aggregated results. Useful for:
        - A/B testing models
        - Comparing response quality
        - Cost/latency benchmarking

        Args:
            prompt: User prompt/query
            models_list: List of model configs, each with 'provider' and 'model' keys
                        Example: [
                            {"provider": "openai", "model": "gpt-4"},
                            {"provider": "gemini", "model": "gemini-pro"}
                        ]
            context: Optional UserContext with conversation history
            timeout_s: Per-model timeout in seconds (default: 60)
            **kwargs: Additional parameters passed to get_completion()

        Returns:
            MultiUnifiedResponse with responses from all models

        Example:
            >>> orchestrator = CortexOrchestrator()
            >>> models = [
            ...     {"provider": "openai", "model": "gpt-3.5-turbo"},
            ...     {"provider": "gemini", "model": "gemini-pro"}
            ... ]
            >>> result = orchestrator.compare(
            ...     prompt="What is Python?",
            ...     models_list=models
            ... )
            >>> for resp in result.responses:
            ...     print(f"{resp.provider}/{resp.model}: {resp.text[:100]}")
        """
        logger.debug(
            f"Processing compare request",
            extra={"extra_fields": {
                "model_count": len(models_list),
                "prompt_length": len(prompt),
                "has_context": context is not None
            }}
        )

        # Initialize clients for all models
        clients = []
        for model_config in models_list:
            try:
                provider = model_config.get("provider")
                model = model_config.get("model")

                if not provider or not model:
                    logger.warning(
                        "Invalid model config - missing provider or model",
                        extra={"extra_fields": {"config": model_config}}
                    )
                    continue

                client = self._get_client(provider, model)
                clients.append(client)

            except Exception as e:
                logger.error(
                    f"Failed to initialize client for {model_config}: {e}",
                    extra={"extra_fields": {
                        "provider": model_config.get("provider"),
                        "model": model_config.get("model"),
                        "error": str(e)
                    }}
                )

        if not clients:
            raise ValueError("No valid clients could be initialized from models_list")

        # Build messages from context
        if context and context.conversation_history:
            messages = context.get_messages()
            messages.append({"role": "user", "content": prompt})
        else:
            messages = [{"role": "user", "content": prompt}]

        # Use MultiModelOrchestrator for parallel execution
        result = self._multi_orchestrator.get_comparisons_sync(
            prompt=prompt,
            clients=clients,
            timeout_s=timeout_s,
            messages=messages,
            **kwargs
        )

        logger.info(
            "Compare request completed",
            extra={"extra_fields": {
                "request_group_id": result.request_group_id,
                "success_count": result.success_count,
                "error_count": result.error_count,
                "total_tokens": result.total_tokens,
                "total_cost": result.total_cost
            }}
        )

        return result

    def create_token_tracker(
        self,
        model_type: str,
        model_name: Optional[str] = None
    ) -> TokenTracker:
        """
        Create a TokenTracker for session-level tracking.

        Args:
            model_type: Provider type
            model_name: Optional model name

        Returns:
            Initialized TokenTracker instance
        """
        return TokenTracker(model_type=model_type, model_name=model_name)

    def create_cost_calculator(
        self,
        model_type: str,
        model_name: Optional[str] = None
    ) -> CostCalculator:
        """
        Create a CostCalculator for session-level cost tracking.

        Args:
            model_type: Provider type
            model_name: Optional model name

        Returns:
            Initialized CostCalculator instance
        """
        if not model_name:
            # Get default model name for the provider
            if model_type.lower() == 'openai':
                model_name = os.getenv('DEFAULT_OPENAI_MODEL', 'gpt-3.5-turbo')
            elif model_type.lower() == 'gemini':
                model_name = os.getenv('DEFAULT_GEMINI_MODEL', 'gemini-2.5-flash-lite')
            elif model_type.lower() == 'deepseek':
                model_name = os.getenv('DEFAULT_DEEPSEEK_MODEL', 'deepseek-chat')
            elif model_type.lower() == 'grok':
                model_name = os.getenv('DEFAULT_GROK_MODEL', 'grok-4-latest')

        return CostCalculator(model_type=model_type, model_name=model_name)