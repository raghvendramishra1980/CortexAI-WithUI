# OpenAIProject - Quick Navigation

## File Locations by Feature

### Want to modify API behavior?
→ `api/base_client.py` (base class)
→ `api/{provider}_client.py` (specific provider)

### Want to change token tracking?
→ `utils/token_tracker.py`

### Want to change cost calculation?
→ `utils/cost_calculator.py`
→ `config/pricing.py` (update prices here)

### Want to add a new model/provider?
1. Create `api/new_provider_client.py`
2. Add pricing to `config/pricing.py`
3. Update `main.py` initialize_client()
4. Update `.env.example`

### Want to modify the CLI interface?
→ `main.py` (chat loop, commands, display)

### Want to configure the app?
→ `.env` (API keys, MODEL_TYPE)

## Don't Touch Unless Necessary
- `tests/` - Test suite
- `venv/` - Virtual environment
- `.gitignore` - Git configuration
- `requirements.txt` - Dependencies

## Key Concepts
- **All providers use OpenAI SDK** (with different base URLs)
- **Cost calculation is separate from token tracking** (by design)
- **Pricing is centralized** (single source of truth)