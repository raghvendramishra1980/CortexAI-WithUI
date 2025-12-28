import os
import threading
import time
import sys
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from datetime import datetime

# Load environment variables first
load_dotenv()

# Import clients based on configuration
MODEL_TYPE = os.getenv('MODEL_TYPE', 'openai').lower()

class TokenTracker:
    """Track token usage across multiple API calls."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all token counters."""
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.requests = 0
    
    def update(self, usage: Optional[Dict[str, int]]):
        """Update token counters with usage from an API call."""
        if not usage:
            return
            
        self.requests += 1
        self.total_prompt_tokens += usage.get('prompt_tokens', 0)
        self.total_completion_tokens += usage.get('completion_tokens', 0)
        self.total_tokens += usage.get('total_tokens', 0)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of token usage."""
        return {
            'requests': self.requests,
            'prompt_tokens': self.total_prompt_tokens,
            'completion_tokens': self.total_completion_tokens,
            'total_tokens': self.total_tokens,
            'timestamp': datetime.now().isoformat()
        }

def main():
    # Initialize token tracker
    token_tracker = TokenTracker()
    
    try:
        # Initialize the appropriate client based on MODEL_TYPE
        if MODEL_TYPE == 'openai':
            from api.openai_client import OpenAIClient
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
                
            client = OpenAIClient(api_key=api_key)
            default_model = os.getenv('DEFAULT_OPENAI_MODEL', 'gpt-3.5-turbo')
            print(f"Initialized OpenAI client with model: {default_model}")
            
        elif MODEL_TYPE == 'gemini':
            from api.google_gemini_client import GeminiClient
            from utils.model_utils import ModelUtils
            
            api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_GEMINI_API_KEY not found in environment variables")
                
            model_name = os.getenv('DEFAULT_GEMINI_MODEL', 'gemini-2.5-flash-lite')
            
            # List available models (one-time operation before initializing main client)
            ModelUtils.list_available_models(api_key=api_key, current_model=model_name)
            
            # Initialize the main client for chat functionality
            client = GeminiClient(api_key=api_key, model_name=model_name)
            print(f"\nInitialized Gemini client with model: {model_name}")
            
        else:
            raise ValueError(f"Unsupported MODEL_TYPE: {MODEL_TYPE}. Must be 'openai' or 'gemini'")
        
        # Example usage with token tracking
        print("\n=== AI Chat ===")
        print("Type 'exit' to quit or 'stats' to see token usage\n")
        
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ('exit', 'quit'):
                    break
                    
                if user_input.lower() == 'stats':
                    stats = token_tracker.get_summary()
                    print("\n=== Token Usage ===")
                    print(f"Requests: {stats['requests']}")
                    print(f"Prompt tokens: {stats['prompt_tokens']}")
                    print(f"Completion tokens: {stats['completion_tokens']}")
                    print(f"Total tokens: {stats['total_tokens']}")
                    print(f"Last updated: {stats['timestamp']}\n")
                    continue
                
                # Show loading animation in a separate thread
                loading = True
                
                def loading_animation():
                    while loading:
                        for char in '|/-\\':
                            if not loading:
                                break
                            sys.stdout.write(f'\r\033[93mThinking {char}\033[0m')
                            sys.stdout.flush()
                            time.sleep(0.1)
                    # Clear the loading line
                    sys.stdout.write('\r' + ' ' * 20 + '\r')
                    sys.stdout.flush()
                
                # Start the loading animation in a separate thread
                loading_thread = threading.Thread(target=loading_animation)
                loading_thread.daemon = True
                loading_thread.start()
                
                try:
                    # Get completion with token tracking
                    response, usage = client.get_completion(user_input, return_usage=True)
                    
                    # Stop the loading animation
                    loading = False
                    loading_thread.join()
                    
                    if response:
                        print(f"\nAI: {response}")
                        if usage:
                            token_tracker.update(usage)
                            print(f"[Tokens used: {usage.get('total_tokens', 'N/A')}]\n")
                except Exception as e:
                    # Ensure loading is stopped even if there's an error
                    loading = False
                    loading_thread.join()
                    raise e
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error initializing client: {str(e)}")
        return
    
    # Print final token usage
    if token_tracker.requests > 0:
        stats = token_tracker.get_summary()
        print("\n=== Final Token Usage ===")
        print(f"Total requests: {stats['requests']}")
        print(f"Total prompt tokens: {stats['prompt_tokens']}")
        print(f"Total completion tokens: {stats['completion_tokens']}")
        print(f"Total tokens used: {stats['total_tokens']}")

if __name__ == "__main__":
    main()