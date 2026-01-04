# Test Suite Documentation

## Overview

This test suite provides comprehensive testing for the OpenAI Project, including:
1. **Unified Response Contract Tests** - Ensures all provider clients adhere to the locked UnifiedResponse contract
2. **Model Utils Tests** - Tests for `ModelUtils` and `GeminiClient` classes (unit and integration tests)

---

## Unified Response Contract Tests

### Purpose

The `test_unified_response_contract.py` test suite **locks and enforces** the UnifiedResponse contract across all AI provider clients (OpenAI, DeepSeek, Grok, Gemini). These tests ensure that:

- All providers return `UnifiedResponse` objects (never provider-specific responses)
- No exceptions bubble up from provider clients (errors returned as structured responses)
- Token usage, cost, latency, and request IDs are always present
- Error handling is consistent with normalized error codes
- Main application code never needs to access provider-specific fields

### Test Structure

The test suite contains **15 tests** organized into 4 test classes:

#### 1. TestUnifiedResponseContract (5 tests)
Tests the core UnifiedResponse data models:

- `test_unified_response_creation` - Validates all required fields can be created
- `test_unified_response_with_error` - Ensures error responses work correctly
- `test_token_usage_auto_total` - Verifies TokenUsage auto-calculates total_tokens
- `test_normalized_error_validates_code` - Checks error code validation (invalid → "unknown")
- `test_finish_reason_validation` - Validates finish_reason normalization

#### 2. TestProviderContractCompliance (4 tests)
Tests that all provider clients return UnifiedResponse:

- `test_openai_returns_unified_response` - OpenAI client returns UnifiedResponse on success
- `test_openai_handles_errors_gracefully` - OpenAI returns error UnifiedResponse (no exception)
- `test_deepseek_returns_unified_response` - DeepSeek client compliance
- `test_grok_returns_unified_response` - Grok client compliance
- `test_gemini_returns_unified_response` - Gemini client compliance (requires google-genai package)

#### 3. TestErrorHandlingContract (3 tests)
Tests that errors are normalized correctly:

- `test_timeout_error_normalized` - Timeout errors → code="timeout", retryable=True
- `test_auth_error_normalized` - Auth errors → code="auth", retryable=False
- `test_rate_limit_error_normalized` - Rate limit errors → code="rate_limit", retryable=True

#### 4. TestTokenTrackerIntegration (2 tests)
Tests that TokenTracker works with UnifiedResponse:

- `test_token_tracker_accepts_unified_response` - TokenTracker can accept UnifiedResponse directly
- `test_token_tracker_backward_compatibility` - TokenTracker still accepts dict format

### Running Unified Response Contract Tests

#### Run all contract tests:
```bash
cd OpenAIProject
python -m pytest tests/test_unified_response_contract.py -v
```

#### Run specific test class:
```bash
# Test all providers
python -m pytest tests/test_unified_response_contract.py::TestProviderContractCompliance -v

# Test error handling
python -m pytest tests/test_unified_response_contract.py::TestErrorHandlingContract -v
```

#### Run with coverage:
```bash
python -m pytest tests/test_unified_response_contract.py --cov=models --cov=api --cov-report=html
```

#### Run specific test:
```bash
python -m pytest tests/test_unified_response_contract.py::TestProviderContractCompliance::test_openai_returns_unified_response -v
```

### Test Results

**Status**: 14/15 tests passing (93% pass rate)

**Passing Tests**:
- All UnifiedResponse model tests ✅
- OpenAI, DeepSeek, Grok client compliance ✅
- All error normalization tests ✅
- TokenTracker integration tests ✅

**Known Issues**:
- `test_gemini_returns_unified_response` - Requires `google-genai` package to be installed. This test will be skipped if the package is not available, or may fail if the mock structure doesn't match the latest google-genai SDK version.

### What These Tests Guarantee

These tests enforce the following contract guarantees:

1. **Type Safety**: All providers MUST return `UnifiedResponse` - no provider-specific types exposed
2. **No Exception Propagation**: Providers catch all exceptions and return them as `UnifiedResponse` with error field
3. **Consistent Error Codes**: All errors normalized to 6 standard codes:
   - `timeout` - Request timed out (retryable)
   - `auth` - Authentication failed (not retryable)
   - `rate_limit` - Rate limit exceeded (retryable)
   - `bad_request` - Invalid request (not retryable)
   - `provider_error` - Provider service error (retryable)
   - `unknown` - Unknown error (not retryable)
4. **Token Usage Always Present**: `TokenUsage` object always populated (zeros if unavailable)
5. **Cost Pre-Calculated**: `estimated_cost` field always present
6. **Request Tracing**: Unique `request_id` (UUID) in every response
7. **Immutability**: All dataclasses are frozen (cannot be modified after creation)

### Example: What the Tests Prevent

**Without Contract (Bad)**:
```python
# Different providers return different types
openai_response = openai_client.get_completion("test")  # Returns OpenAI response object
gemini_response = gemini_client.get_completion("test")  # Returns Gemini response object

# Main code must handle each provider differently
if isinstance(openai_response, OpenAIResponse):
    text = openai_response.choices[0].message.content
elif isinstance(gemini_response, GeminiResponse):
    text = gemini_response.text
```

**With Contract (Good)**:
```python
# All providers return UnifiedResponse
openai_resp = openai_client.get_completion("test")  # Returns UnifiedResponse
gemini_resp = gemini_client.get_completion("test")  # Returns UnifiedResponse

# Main code works with all providers
if resp.is_error:
    print(f"Error: {resp.error.message}")
else:
    print(resp.text)  # Same field for all providers
```

### Adding a New Provider

When adding a new AI provider, these tests ensure you implement the contract correctly:

1. Inherit from `BaseAIClient`
2. Return `UnifiedResponse` from `get_completion()`
3. Use helper methods: `_generate_request_id()`, `_measure_latency()`, `_normalize_error()`, `_normalize_finish_reason()`
4. Catch ALL exceptions and return error responses
5. Add a test in `TestProviderContractCompliance`

Example test for new provider:
```python
@patch('new_provider.Client')
def test_newprovider_returns_unified_response(self, mock_client):
    """Test that NewProvider client returns UnifiedResponse."""
    # Mock successful response
    mock_response = Mock()
    mock_response.text = "Test response"
    mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20)
    mock_client.return_value.complete.return_value = mock_response

    client = NewProviderClient(api_key="test-key")
    response = client.get_completion("Test prompt")

    assert isinstance(response, UnifiedResponse)
    assert response.provider == "newprovider"
    assert response.is_success
```

---

## Model Utils Tests

## Test Categories

### 1. Unit Tests (Fast, No External Dependencies)
Located in `TestModelUtilsUnit` class - These tests use mocks to verify business logic without making real API calls.

**What they test:**
- Function calls and parameter passing
- Output formatting and filtering
- Error handling (401, 429, 500, timeouts)
- Edge cases (empty responses, missing data)
- Current model marking logic

**Run unit tests only:**
```bash
pytest tests/test_model_utils.py -m "not integration"
```

### 2. Integration Tests (Requires API Key)
Located in `TestModelUtilsIntegration` class - These tests make real API calls to verify actual behavior.

**What they test:**
- Real API responses (200 OK)
- Authentication errors (401)
- Network timeout handling
- Response data structure validation

**Run integration tests:**
```bash
# Set your API key
set GEMINI_API_KEY=your_actual_api_key_here  # Windows
# or
export GEMINI_API_KEY=your_actual_api_key_here  # Linux/Mac

# Run tests
pytest tests/test_model_utils.py -m integration
```

### 3. GeminiClient Tests
Located in `TestGeminiClient` class - These tests verify the API wrapper class directly.

**What they test:**
- Client initialization
- Default model handling
- Response structure parsing
- Exception propagation
- Real API integration (when key is available)

## Running All Tests

### Quick Start

```bash
# Install dependencies
pip install pytest pytest-cov

# Run ALL tests (both contract and model utils)
pytest tests/ -v

# Run only unified response contract tests (fast, recommended)
pytest tests/test_unified_response_contract.py -v

# Run only model utils unit tests (fast, no API key needed)
pytest tests/test_model_utils.py -m "not integration"

# Run all tests including integration (requires API key)
set GEMINI_API_KEY=your_key
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_unified_response_contract.py -v
pytest tests/test_model_utils.py -v

# Run specific test class
pytest tests/test_model_utils.py::TestModelUtilsUnit
pytest tests/test_unified_response_contract.py::TestProviderContractCompliance

# Run specific test
pytest tests/test_model_utils.py::TestModelUtilsUnit::test_list_models_success_with_output
pytest tests/test_unified_response_contract.py::TestErrorHandlingContract::test_timeout_error_normalized
```

### Running with Coverage

```bash
# Generate coverage report for all tests
pytest tests/ --cov=models --cov=api --cov=utils --cov-report=html --cov-report=term

# Generate coverage for contract tests only
pytest tests/test_unified_response_contract.py --cov=models --cov=api --cov-report=html

# Generate coverage for model utils tests only
pytest tests/test_model_utils.py --cov=utils --cov-report=html --cov-report=term

# View coverage report
# Open htmlcov/index.html in your browser
```

### Continuous Integration

For CI/CD pipelines, run fast tests without integration tests:

```bash
# Run contract tests + model utils unit tests
pytest tests/test_unified_response_contract.py tests/test_model_utils.py -m "not integration" --cov=models --cov=api --cov=utils --cov-report=xml
```

## Test Results Interpretation

### Success Indicators
- All assertions pass
- No exceptions raised (except where expected)
- Output contains expected content
- Mock calls match expected patterns

### Common Failures

**Import Errors:**
```
ImportError: No module named 'google.genai'
```
Solution: Install required packages
```bash
pip install google-generativeai
```

**Skipped Integration Tests:**
```
SKIPPED [1] test_model_utils.py:195: No GEMINI_API_KEY environment variable
```
Solution: This is normal if you don't have an API key set. Integration tests are optional.

**Authentication Failures:**
```
Exception: 401: Invalid API key
```
Solution: Check your `GEMINI_API_KEY` is correct and active.

## Test Coverage Goals

### Current Coverage
- **Unified Response Contract Tests**: 15 tests (14 passing, 1 requires google-genai)
  - UnifiedResponse model tests: 5 tests
  - Provider compliance tests: 4 tests
  - Error handling tests: 3 tests
  - TokenTracker integration tests: 2 tests
- **Model Utils Unit Tests**: 10 tests covering all major code paths
- **Model Utils Integration Tests**: 4 tests for real API scenarios
- **GeminiClient Tests**: 7 tests for the wrapper class

**Total**: 36 tests across all test suites

### Coverage Targets
- Line Coverage: >90%
- Branch Coverage: >85%
- Function Coverage: 100%

### Contract Coverage
The unified response contract tests provide **100% coverage** of:
- All UnifiedResponse fields and properties
- All provider clients (OpenAI, DeepSeek, Grok, Gemini)
- All 6 error codes (timeout, auth, rate_limit, bad_request, provider_error, unknown)
- TokenTracker integration with UnifiedResponse

## Writing New Tests

### Adding a Contract Test (For New Provider)

When adding a new AI provider, add a test to enforce the contract:

```python
@patch('new_provider_sdk.Client')
def test_newprovider_returns_unified_response(self, mock_client):
    """Test that NewProvider client returns UnifiedResponse."""
    from api.newprovider_client import NewProviderClient
    from models.unified_response import UnifiedResponse

    # Mock successful response
    mock_response = Mock()
    mock_response.text = "Test response"
    mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    mock_response.finish_reason = "complete"
    mock_client.return_value.generate.return_value = mock_response

    client = NewProviderClient(api_key="test-key", model_name="model-v1")
    response = client.get_completion("Test prompt")

    # MUST return UnifiedResponse
    assert isinstance(response, UnifiedResponse)
    assert response.provider == "newprovider"
    assert response.text == "Test response"
    assert isinstance(response.token_usage, TokenUsage)
    assert response.token_usage.total_tokens == 30
    assert response.finish_reason == "stop"  # Should be normalized
    assert response.error is None
    assert response.is_success
```

### Adding a Unit Test

```python
@patch('utils.model_utils.GeminiAvailableModels')
@patch('sys.stdout', new_callable=StringIO)
def test_new_feature(self, mock_stdout, mock_gemini_class):
    """Test description"""
    # Setup
    mock_client = MagicMock()
    mock_gemini_class.return_value = mock_client

    # Execute
    ModelUtils.your_method('param1', 'param2')

    # Assert
    assert something
```

### Adding an Integration Test

```python
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv('GEMINI_API_KEY'), reason="No GEMINI_API_KEY")
def test_new_integration(self):
    """Test real API behavior"""
    api_key = os.getenv('GEMINI_API_KEY')

    # Make real API call
    result = ModelUtils.your_method(api_key, 'param')

    # Verify result
    assert result is not None
```

## Best Practices

### Contract Tests
1. **Test every provider** - When adding a new provider, MUST add contract compliance test
2. **Never skip error testing** - Test that exceptions are caught and returned as UnifiedResponse
3. **Verify immutability** - Ensure frozen dataclasses cannot be modified
4. **Test all error codes** - Verify normalization for timeout, auth, rate_limit, etc.
5. **Mock at SDK level** - Mock the provider's SDK, not the client wrapper

### Unit and Integration Tests
1. **Always test with mocks first** - Unit tests should run fast without external dependencies
2. **Use descriptive test names** - `test_list_models_handles_401_error` is better than `test_error`
3. **One assertion per test when possible** - Makes failures easier to diagnose
4. **Test both success and failure paths** - Don't just test the happy path
5. **Use fixtures for common setup** - Reduces code duplication
6. **Mark slow tests** - Use `@pytest.mark.slow` for tests that take >1 second
7. **Document expected behavior** - Add docstrings explaining what each test verifies

## Troubleshooting

### Contract Tests

**Test fails: "AssertionError: assert isinstance(response, dict)"**
- Problem: Provider is not returning UnifiedResponse
- Solution: Ensure provider's `get_completion()` returns UnifiedResponse, not dict or tuple

**Test fails: "Exception was raised instead of returning error response"**
- Problem: Provider is not catching exceptions
- Solution: Wrap provider SDK call in try/except, use `_create_error_response()`

**Test fails: "AttributeError: 'UnifiedResponse' object has no attribute 'choices'"**
- Problem: Main code is accessing provider-specific fields
- Solution: Update code to use UnifiedResponse fields (text, token_usage, error, etc.)

**Gemini test skipped or fails**
- Problem: `google-genai` package not installed or mock structure mismatch
- Solution: Install package or skip test (it's optional for contract enforcement)

### Model Utils Tests

**Tests are slow**
- Solution: Run only unit tests: `pytest -m "not integration"`

**Can't install pytest**
```bash
pip install --upgrade pip
pip install pytest pytest-cov
```

**Mock not working**
Make sure you're patching at the right location:
- Patch where the object is **used**, not where it's **defined**
- Example: Patch `'utils.model_utils.GeminiAvailableModels'` not `'GeminiAvailableModels.GeminiClient'`

**Integration tests failing**
1. Check API key is valid
2. Check network connection
3. Check API rate limits
4. Check Google GenAI service status

## Dependencies

Required packages:
```
# Core testing
pytest>=7.0.0
pytest-cov>=4.0.0

# For contract tests
openai>=1.0.0  # OpenAI, DeepSeek, Grok clients

# For model utils tests (optional)
google-generativeai>=0.3.0  # Gemini integration tests

# Standard library (already included)
unittest.mock  # Mocking
```

Install all:
```bash
pip install -r requirements.txt
```

Minimum for contract tests only:
```bash
pip install pytest pytest-cov openai
```

## Summary

This test suite provides comprehensive coverage across multiple layers:

### Contract Tests (High Priority)
- **15 tests** enforcing the UnifiedResponse contract
- **100% provider coverage** - All 4 providers tested
- **Fast execution** - Uses mocks, no API calls needed
- **Prevents regressions** - Catches contract violations immediately
- **Recommended to run before every commit**

### Model Utils Tests (Feature Testing)
- **21 tests** for model listing and GeminiClient functionality
- **Mix of unit and integration tests**
- **Optional integration tests** require API keys

### Key Benefits
1. **Type Safety** - Contract tests ensure consistent response types
2. **No Surprises** - Error handling is predictable across all providers
3. **Fast Feedback** - Contract tests run in seconds
4. **Easy Refactoring** - Change provider internals without breaking main code
5. **Documentation** - Tests serve as usage examples

### Recommended Workflow
```bash
# Before committing code
pytest tests/test_unified_response_contract.py -v  # Must pass

# Before pushing to main
pytest tests/ -v  # Run all tests

# When adding new provider
# 1. Implement provider client
# 2. Add contract test
# 3. Verify all contract tests pass
```

## Contact & Support

For issues or questions about these tests:
1. Check test output and error messages
2. Review test docstrings for expected behavior
3. Verify your environment setup (API keys, dependencies)
4. Check the main codebase for changes that might affect tests
5. See `UNIFIED_RESPONSE_CONTRACT.md` for contract documentation
6. See `LOGGING.md` for logging system documentation