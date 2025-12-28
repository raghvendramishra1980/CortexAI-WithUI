import os
from typing import Optional, Dict, Tuple

from google import genai


class GeminiClient:
    """
    A client for interacting with the Google Gemini API (google-genai).
    Handles API calls and response processing.
    """

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the Gemini client with the provided API key and model name.
        """
        try:
            if not api_key:
                raise ValueError("api_key is required")

            # NEW SDK: create a client (no genai.configure in google-genai)
            self.client = genai.Client(api_key=api_key)

            # Respect the model_name passed in (fallback to a sensible default)
            self.model_name = model_name or "gemini-2.5-flash-lite"

        except Exception as e:
            print(f"Error initializing Gemini client: {str(e)}")
            raise

    def get_completion(
            self,
            prompt: str,
            model: str = None,
            return_usage: bool = False
    ) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Get a completion from the Gemini API.

        Args:
            prompt: The input prompt to send to the model
            model: Optional override model name (kept for compatibility)
            return_usage: If True, returns (response_text, usage_dict)

        Returns:
            (response_text, usage_dict_or_none)
        """
        try:
            if not prompt or not prompt.strip():
                return None, None

            model_to_use = model or self.model_name

            response = self.client.models.generate_content(
                model=model_to_use,
                contents=prompt
            )

            text = getattr(response, "text", None)

            if not return_usage:
                return text, None

            # Usage fields can vary depending on API / plan.
            # We'll try to extract something if present, otherwise return zeros.
            usage_dict = {"model": model_to_use}

            usage = getattr(response, "usage", None)
            if usage:
                usage_dict.update({
                    "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(usage, "completion_tokens", 0),
                    "total_tokens": getattr(usage, "total_tokens", 0),
                })
            else:
                usage_dict.update({
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                })

            return text, usage_dict

        except Exception as e:
            print(f"Error getting completion from Gemini: {str(e)}")
            return None, None


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

    # Recommended defaults:
    # - gemini-1.5-flash for fast + cost-effective chat
    # - gemini-1.5-pro for higher reasoning quality
    model_name = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-1.5-flash")

    if not api_key:
        print("Error: GOOGLE_GEMINI_API_KEY not found in environment variables")
    else:
        client = GeminiClient(api_key=api_key, model_name=model_name)
        response, usage = client.get_completion(
            "Hello, how can I help you today?",
            return_usage=True
        )
        print(response)
        print(usage)