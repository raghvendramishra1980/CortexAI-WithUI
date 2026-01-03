# Changelog

All notable changes to OpenAIProject will be documented in this file.

## [Unreleased]

## [2.0.0] - 2026-01-03

### Added
- **Grok (X.AI) Support**: Complete integration with grok-4-latest and other models
- **Cost Tracking System**: Real-time cost calculation with pricing data
  - Created `utils/cost_calculator.py` (separate from token tracking)
  - Created `config/pricing.py` with current pricing for all providers
  - Per-request and cumulative cost display
  - Session statistics with cost breakdown
- **Enhanced Documentation**: Comprehensive README and context files

### Changed
- Updated `TokenTracker` to optionally store model type/name
- Modified `main.py` to support cost tracking alongside token tracking
- Updated `.env` and `.env.example` with Grok configuration

### Technical Details
- Architecture: Token tracking and cost calculation are separate modules
- Pricing: Centralized in `config/pricing.py` (per million tokens)
- All clients use OpenAI SDK with custom base URLs

## [1.0.0] - 2025-12-XX

### Added
- Initial release with OpenAI, Gemini, and DeepSeek support
- Token tracking functionality
- Interactive CLI with loading animations
- Environment-based configuration

---

**Note**: For detailed architecture, see `.claude-context.md` and `PROJECT_MAP.md`