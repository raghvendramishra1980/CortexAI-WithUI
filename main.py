import os
import threading
import time
import sys
from dotenv import load_dotenv
from typing import Optional, Dict, Any, Type

# Load environment variables first
load_dotenv()

# Import clients based on configuration
MODEL_TYPE = os.getenv('MODEL_TYPE', 'openai').lower()

# Import the base client and token tracker
from api.base_client import BaseAIClient
from utils.token_tracker import TokenTracker

def initialize_client(model_type: str) -> BaseAIClient:
    """
    Initialize the appropriate AI client based on the model type.
    
    Args:
        model_type: The type of model to initialize ('openai' or 'gemini')
        
    Returns:
        An instance of the appropriate AI client
        
    Raises:
        ValueError: If the model type is unsupported or required environment variables are missing
    """
    model_type = model_type.lower()
    
    if model_type == 'openai':
        from api.openai_client import OpenAIClient
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        model_name = os.getenv('DEFAULT_OPENAI_MODEL', 'gpt-3.5-turbo')
        client = OpenAIClient(api_key=api_key, model_name=model_name)
        print(f"Initialized OpenAI client with model: {model_name}")
        
    elif model_type == 'gemini':
        from api.google_gemini_client import GeminiClient
        
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY not found in environment variables")
            
        model_name = os.getenv('DEFAULT_GEMINI_MODEL', 'gemini-2.5-flash-lite')
        
        # List available models (one-time operation before initializing main client)
        GeminiClient.list_available_models(api_key=api_key, current_model=model_name)
        
        # Initialize the main client for chat functionality
        client = GeminiClient(api_key=api_key, model_name=model_name)
        print(f"\nInitialized Gemini client with model: {model_name}")
        
    else:
        raise ValueError(f"Unsupported MODEL_TYPE: {model_type}. Must be 'openai' or 'gemini'")
    
    return client


def show_loading_animation(stop_event: threading.Event) -> None:
    """
    Show a loading animation in the console.
    
    Args:
        stop_event: A threading.Event that will be set to stop the animation
    """
    while not stop_event.is_set():
        for char in '|/-\\':
            if stop_event.is_set():
                break
            sys.stdout.write(f'\r\033[93mThinking {char}\033[0m')
            sys.stdout.flush()
            time.sleep(0.1)
    
    # Clear the loading line
    sys.stdout.write('\r' + ' ' * 20 + '\r')
    sys.stdout.flush()


def main():
    # Initialize token tracker
    token_tracker = TokenTracker()
    
    try:
        # Initialize the appropriate client
        client = initialize_client(MODEL_TYPE)
        
        # Start the chat interface
        print("\n=== AI Chat ===")
        print("Type 'exit' to quit, 'stats' to see token usage, or 'help' for commands\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                # Handle commands
                if not user_input:
                    continue
                    
                if user_input.lower() in ('exit', 'quit'):
                    print("\nGoodbye!")
                    break
                    
                if user_input.lower() == 'stats':
                    print("\n=== Token Usage ===")
                    print(token_tracker.format_summary())
                    print(f"Last updated: {token_tracker.get_summary()['timestamp']}\n")
                    continue
                    
                if user_input.lower() == 'help':
                    print("\n=== Available Commands ===")
                    print("help     - Show this help message")
                    print("stats    - Show token usage statistics")
                    print("exit/quit - Exit the program\n")
                    continue
                
                # Show loading animation in a separate thread
                stop_animation = threading.Event()
                loading_thread = threading.Thread(target=show_loading_animation, args=(stop_animation,))
                loading_thread.daemon = True
                loading_thread.start()
                
                try:
                    # Get completion with token tracking
                    response, usage = client.get_completion(user_input, return_usage=True)
                    
                    # Stop the loading animation
                    stop_animation.set()
                    loading_thread.join()
                    
                    if response:
                        print(f"\nAI: {response}")
                        if usage:
                            token_tracker.update(usage)
                            print(f"[Tokens used: {usage.get('total_tokens', 'N/A')}]\n")
                except Exception as e:
                    # Ensure loading is stopped even if there's an error
                    stop_animation.set()
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
    finally:
        # Print final token usage if any requests were made
        if token_tracker.requests > 0:
            print("\n=== Final Token Usage ===")
            print(token_tracker.format_summary())


if __name__ == "__main__":
    main()