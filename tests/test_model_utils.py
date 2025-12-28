from unittest.mock import patch, MagicMock
from utils.model_utils import ModelUtils


class TestModelUtilsAPICalls:
    @patch('GeminiAvailableModels.GeminiClient')  # Patch at the source module
    def test_list_available_models_success_status_code(self, mock_gemini_class):
        # Setup mock
        mock_client = MagicMock()
        mock_gemini_class.return_value = mock_client

        # Setup mock response - should return list of tuples
        mock_models = [
            ("models/gemini-pro", ["generateContent"]),
            ("models/gemini-pro-vision", ["generateContent"])
        ]
        mock_client.list_models.return_value = mock_models

        # Call the method
        ModelUtils.list_available_models('test-api-key', 'gemini-pro')

        # Verify the client was initialized with correct parameters
        mock_gemini_class.assert_called_once_with(api_key='test-api-key', model_name='gemini-pro')

        # Verify list_models was called
        mock_client.list_models.assert_called_once()

    @patch('GeminiAvailableModels.GeminiClient')  # Patch at the source module
    def test_list_available_models_error_status_code(self, mock_gemini_class):
        # Setup mock to raise an exception
        mock_gemini_class.side_effect = Exception("API key invalid")

        # Call the method - it should handle the exception gracefully
        # The function prints a warning but doesn't raise
        ModelUtils.list_available_models('invalid-key', 'gemini-pro')

        # Verify the client was attempted to be initialized
        mock_gemini_class.assert_called_once_with(api_key='invalid-key', model_name='gemini-pro')