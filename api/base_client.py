from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any

class BaseAIClient(ABC):
    """
    Abstract base class for AI model clients.
    All model-specific clients should inherit from this class and implement its methods.
    """
    
    @abstractmethod
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the AI client.
        
        Args:
            api_key: API key for the AI service
            **kwargs: Additional model-specific parameters
        """
        self.api_key = api_key
        self.model_name = kwargs.get('model_name')
    
    @abstractmethod
    def get_completion(self, prompt: str, **kwargs) -> Tuple[str, Optional[Dict[str, int]]]:
        """
        Get a completion from the AI model.
        
        Args:
            prompt: The input prompt to send to the model
            **kwargs: Additional parameters for the API call
            
        Returns:
            A tuple containing:
                - The generated text response
                - A dictionary with token usage information (or None if not available)
        """
        pass
    
    @classmethod
    @abstractmethod
    def list_available_models(cls, api_key: str = None, **kwargs) -> None:
        """
        List all available models for this client.
        
        Args:
            api_key: Optional API key (if not provided during initialization)
            **kwargs: Additional parameters for the API call
        """
        pass
    
    def get_token_usage(self, response: Any) -> Optional[Dict[str, int]]:
        """
        Extract token usage information from the API response.
        This method can be overridden by subclasses if the token usage is in a different format.
        
        Args:
            response: The raw response from the model API
            
        Returns:
            A dictionary with token usage information or None if not available
        """
        # Default implementation returns None
        # Subclasses should override this if they can provide token usage
        return None
