from typing import List, Tuple, Optional

class ModelUtils:
    @staticmethod
    def list_available_models(api_key: str, current_model: str) -> None:
        """
        List all available Gemini models that support content generation.
        
        Args:
            api_key: Google Gemini API key
            current_model: Currently selected model name
        """
        try:
            from GeminiAvailableModels import GeminiClient as GeminiAvailableModels
            
            print("\n=== Fetching Available Gemini Models ===")
            models_client = GeminiAvailableModels(api_key=api_key, model_name=current_model)
            available_models = models_client.list_models()
            
            print("\n=== Available Gemini Models ===")
            for model, methods in available_models:
                if methods and 'generateContent' in methods:  # Only show models that support generation
                    current = " (current)" if model.endswith(current_model) else ""
                    print(f"- {model}{current}")
            print("\nNote: Only models supporting 'generateContent' are shown")
            
        except Exception as e:
            print(f"\n[Warning] Could not list available models: {str(e)}")
