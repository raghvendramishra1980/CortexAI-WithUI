# AI Chat Interface

A Python command-line application that interacts with multiple AI providers (OpenAI and Google Gemini) to provide conversational AI responses.

## Features

- Interactive command-line interface
- Support for multiple AI providers (OpenAI and Google Gemini)
- Easy switching between different AI models
- Environment-based configuration
- Error handling and user-friendly messages
- Colored console output
- Token usage tracking (for supported models)

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (if using OpenAI models)
- Google Gemini API key (if using Google Gemini models)

## Setup

1. Clone the repository or create a new directory for the project
2. Navigate to the project directory
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
6. Edit the `.env` file and configure your preferred settings:
   - Set `MODEL_TYPE` to either 'openai' or 'gemini'
   - Add your OpenAI API key if using OpenAI
   - Add your Google Gemini API key if using Gemini

## Usage

1. First, install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Once running, you can:
   - Type your message and press Enter to get a response
   - Type 'exit' or 'quit' to end the session
   - Press Ctrl+C to exit at any time

## Configuration

The application is configured using environment variables in the `.env` file:

```ini
# Choose which model to use: 'openai' or 'gemini'
MODEL_TYPE=openai

# OpenAI API Configuration (required if MODEL_TYPE=openai)
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API Configuration (required if MODEL_TYPE=gemini)
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key_here

# Model Configuration
# For OpenAI models (e.g., gpt-3.5-turbo, gpt-4)
DEFAULT_MODEL=gpt-3.5-turbo
```

## Switching Between AI Providers

To switch between OpenAI and Google Gemini, simply update the `MODEL_TYPE` in your `.env` file and provide the appropriate API key.

## Project Structure

```
.
├── .env.example           # Example environment configuration
├── .gitignore            # Git ignore file
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── config/               # Configuration management
│   ├── __init__.py
│   └── config.py         # Configuration class
├── api/                  # API client implementations
│   ├── __init__.py
│   ├── openai_client.py  # OpenAI client
│   └── google_gemini_client.py  # Google Gemini client
└── main.py              # Main application
```

## Getting API Keys

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API keys
4. Create a new secret key

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Sign in with your Google account
3. Click on "Get API Key"
4. Create an API key in Google AI Studio

## Troubleshooting

- **Missing API Key**: Ensure you've set the correct API key in your `.env` file for the selected model type.
- **Authentication Errors**: Double-check your API keys and ensure they're correctly set in the `.env` file.
- **Model Not Available**: Make sure you have access to the selected model with your API key.

```
OpenAIProject/
├── .env.example          # Example environment variables
├── requirements.txt      # Project dependencies
├── main.py               # Main application entry point
├── api/
│   └── openai_client.py  # OpenAI API client
└── config/
    ├── __init__.py
    └── config.py         # Configuration management
```

## Configuration

The application can be configured using the following environment variables in the `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DEFAULT_MODEL`: The model to use (default: gpt-3.5-turbo)

## Error Handling

The application includes basic error handling for:
- Missing API key
- API request failures
- User interruptions (Ctrl+C)
- Invalid inputs

## License

This project is open source and available under the MIT License.
