import openai
from typing import Optional


class OpenAIClient:
    """
    A client for interacting with the OpenAI API.
    Handles API calls and response processing.
    """

    def __init__(self, api_key: str):
        """Initialize the OpenAI client with the provided API key."""
        self.client = openai.OpenAI(api_key=api_key)

    def get_completion(self, prompt: str, model: str = "gpt-3.5-turbo", return_usage: bool = False) -> tuple[
        Optional[str], Optional[dict]]:
        """
        Get a completion from the OpenAI API with optional token usage tracking.
        
        Args:
            prompt: The input prompt to send to the model
            model: The model to use for completion (default: gpt-3.5-turbo)
            return_usage: If True, returns a tuple of (response, usage_dict)
            
        Returns:
            If return_usage is False: The generated text response or None if an error occurs
            If return_usage is True: A tuple of (response, usage_dict) where usage_dict contains
                                   token usage information (prompt_tokens, completion_tokens, total_tokens)
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )

            if return_usage and hasattr(response, 'usage'):
                usage = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
                return response.choices[0].message.content, usage

            return response.choices[0].message.content, None

        except Exception as e:
            print(f"Error getting completion: {str(e)}")
            return None, None
