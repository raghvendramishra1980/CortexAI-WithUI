# AI Chat Interface

A Python command-line application that provides an interactive chat interface with multiple AI providers, featuring token usage tracking and real-time cost estimation.

## Features

- **Multi-Provider Support**: OpenAI, Google Gemini, DeepSeek, and Grok (X.AI)
- **Interactive CLI**: User-friendly command-line interface with loading animations
- **Token Tracking**: Real-time monitoring of token usage (prompt, completion, and total)
- **Cost Calculation**: Automatic cost estimation based on current pricing for all models
- **Easy Model Switching**: Simple configuration to switch between providers and models
- **Session Statistics**: View cumulative token usage and costs during your session
- **Environment-Based Configuration**: Secure API key management using `.env` files

## Prerequisites

- Python 3.8 or higher
- API key for your chosen provider:
  - OpenAI API key (for GPT models)
  - Google Gemini API key (for Gemini models)
  - DeepSeek API key (for DeepSeek models)
  - Grok API key (for Grok models from X.AI)

## Installation

1. **Clone the repository** (or create a new directory):
   ```bash
   cd OpenAIProject
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

5. **Edit `.env` file** with your API keys and preferred model:
   ```ini
   # Choose: 'openai', 'gemini', 'deepseek', or 'grok'
   MODEL_TYPE=deepseek

   # Add your API key(s)
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   GROK_API_KEY=your_grok_api_key_here

   # Set default models (optional)
   DEFAULT_OPENAI_MODEL=gpt-3.5-turbo
   DEFAULT_GEMINI_MODEL=gemini-2.5-flash-lite
   DEFAULT_DEEPSEEK_MODEL=deepseek-chat
   DEFAULT_GROK_MODEL=grok-4-latest
   ```

## Usage

1. **Run the application**:
   ```bash
   python main.py
   ```

2. **Available commands** during chat:
   - Type your message and press Enter to get a response
   - `stats` - View token usage and cost statistics for current session
   - `help` - Show available commands
   - `exit` or `quit` - End the session
   - `Ctrl+C` - Exit at any time

3. **Example session**:
   ```
   === AI Chat ===
   Type 'exit' to quit, 'stats' to see token usage, or 'help' for commands

   You: Hello, how are you?

   AI: I'm doing well, thank you for asking! How can I help you today?
   [Tokens: 45 | Cost: $0.000023]

   You: stats

   === Session Statistics ===
   Requests: 1
   Prompt tokens: 12
   Completion tokens: 33
   Total tokens: 45

   Input cost: $0.000003
   Output cost: $0.000020
   Total cost: $0.000023

   Last updated: 2026-01-02T23:45:12.123456
   ```

## Supported Models

### OpenAI
- **GPT-4**: `gpt-4`, `gpt-4-turbo`, `gpt-4-0125-preview`
- **GPT-3.5**: `gpt-3.5-turbo`, `gpt-3.5-turbo-0125`
- **Pricing**: $0.50-$60.00 per million tokens

### Google Gemini
- **Gemini 2.5**: `gemini-2.5-flash-lite`
- **Gemini 1.5**: `gemini-1.5-flash`, `gemini-1.5-pro`
- **Pricing**: $0.05-$5.00 per million tokens

### DeepSeek
- **DeepSeek V3**: `deepseek-chat` (general conversation)
- **DeepSeek R1**: `deepseek-reasoner` (advanced reasoning)
- **Pricing**: $0.27-$2.19 per million tokens

### Grok (X.AI)
- **Grok 4**: `grok-4-latest` (latest model)
- **Grok 2**: `grok-2`, `grok-2-mini`
- **Pricing**: $0.50-$15.00 per million tokens

## Project Structure

```
OpenAIProject/
├── .env                      # Your configuration (not in git)
├── .env.example              # Example configuration template
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── requirements.txt         # Python dependencies
├── pytest.ini              # Pytest configuration
├── main.py                 # Main application entry point
│
├── api/                    # API client implementations
│   ├── __init__.py
│   ├── base_client.py      # Abstract base class for all clients
│   ├── openai_client.py    # OpenAI API client
│   ├── google_gemini_client.py  # Google Gemini client
│   ├── deepseek_client.py  # DeepSeek API client
│   └── grok_client.py      # Grok (X.AI) API client
│
├── config/                 # Configuration management
│   ├── __init__.py
│   ├── config.py           # Configuration class
│   └── pricing.py          # Model pricing data
│
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── token_tracker.py    # Token usage tracking
│   └── cost_calculator.py  # Cost calculation logic
│
└── tests/                  # Test suite
    ├── __init__.py
    └── ...
```

## Architecture

The application follows a clean architecture with clear separation of concerns:

### API Clients
All API clients inherit from `BaseAIClient` and implement:
- `get_completion()` - Get AI response with token tracking
- `list_available_models()` - List available models for the provider

### Token Tracking
`TokenTracker` class tracks:
- Number of requests
- Prompt (input) tokens
- Completion (output) tokens
- Total tokens used

### Cost Calculation
`CostCalculator` class maintains **separation from token tracking**:
- Stores pricing information for all models
- Calculates per-request costs
- Maintains cumulative session costs
- Formats costs for display

**Design Principle**: Token tracking and cost calculation are separate modules that can work independently, maintaining clean abstraction.

## Getting API Keys

### OpenAI
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new secret key

### Google Gemini
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Sign in with Google account
3. Click "Get API Key"
4. Create an API key

### DeepSeek
1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Generate a new API key

### Grok (X.AI)
1. Visit [X.AI Console](https://console.x.ai/)
2. Sign up or log in
3. Navigate to API section
4. Create a new API key

## Configuration Options

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MODEL_TYPE` | AI provider to use | `openai`, `gemini`, `deepseek`, `grok` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `GOOGLE_GEMINI_API_KEY` | Gemini API key | `AIza...` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | `sk-...` |
| `GROK_API_KEY` | Grok API key | `xai-...` |
| `DEFAULT_OPENAI_MODEL` | Default OpenAI model | `gpt-3.5-turbo` |
| `DEFAULT_GEMINI_MODEL` | Default Gemini model | `gemini-2.5-flash-lite` |
| `DEFAULT_DEEPSEEK_MODEL` | Default DeepSeek model | `deepseek-chat` |
| `DEFAULT_GROK_MODEL` | Default Grok model | `grok-4-latest` |

### Switching Providers

To switch between AI providers:
1. Open `.env` file
2. Change `MODEL_TYPE` to your desired provider
3. Ensure the corresponding API key is set
4. (Optional) Set the default model for that provider
5. Restart the application

## Cost Tracking Details

The application calculates costs based on:
- **Input tokens** (prompt): Charged at input rate
- **Output tokens** (completion): Charged at output rate (typically higher)
- **Current pricing** (as of January 2026)

**Note**: Actual costs may vary. Always verify pricing on the provider's official website. This is an estimation tool for reference.

## Troubleshooting

### Common Issues

**Missing API Key Error**
```
Error: OPENAI_API_KEY not found in environment variables
```
**Solution**: Add your API key to the `.env` file for the selected provider.

**Authentication Error**
```
Error: 401 Unauthorized
```
**Solution**: Verify your API key is correct and active.

**Model Not Available**
```
Error: Model 'xyz' not found
```
**Solution**: Check that the model name is correct and you have access to it.

**No Credits/Quota Error**
```
Error: 403 - No credits available
```
**Solution**: Add credits to your account or check your usage limits.

### Getting Help

If you encounter issues:
1. Check the error message displayed
2. Verify your `.env` configuration
3. Ensure your API key has sufficient credits
4. Check the provider's status page for outages

## Development

### Running Tests
```bash
pytest
```

### Adding a New Provider

1. Create a new client in `api/` that inherits from `BaseAIClient`
2. Implement required methods: `get_completion()` and `list_available_models()`
3. Add pricing information to `config/pricing.py`
4. Update `main.py` to include the new provider in `initialize_client()`
5. Update `.env.example` with new configuration options

## License

This project is open source and available under the MIT License.

## Acknowledgments

- OpenAI for GPT models
- Google for Gemini models
- DeepSeek for DeepSeek models
- X.AI for Grok models

---

**Last Updated**: January 2026