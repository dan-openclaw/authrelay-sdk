# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024

### Added
- Initial release of AuthRelay Agent SDK
- TypeScript/JavaScript SDK (`authrelay` npm package)
  - `AuthRelay` class for easy authentication requests
  - `RelaySession` class for advanced session management
  - Event-driven architecture with EventEmitter
  - Full TypeScript type exports
  - Zero external dependencies
  - ESM and CommonJS support
  - Exponential backoff polling (2s → 3s → 5s cap)
- Python SDK (`authrelay` pip package)
  - Synchronous `AuthRelay` client
  - Asynchronous `AsyncAuthRelay` client
  - `RelaySession` for event-driven polling
  - Zero dependencies for sync client
  - Optional `aiohttp` dependency for async
  - Dataclass-based result types
  - Full Python 3.8+ support
- Comprehensive documentation
  - SDK READMEs with quickstart and API reference
  - Development guide
  - Error handling guidance
  - Configuration examples
- Test scripts for both SDKs
- MIT License
- .gitignore for both Node.js and Python

### Features
- **Zero dependencies** for synchronous clients
  - TypeScript: uses native `fetch`
  - Python: uses `urllib.request`
- **Human-in-the-loop authentication** workflow
- **Event-driven polling** with exponential backoff
- **Configurable base URL** for self-hosted instances
- **Helpful error messages** with context
- **API key validation** with format warnings
- **Timeout handling** with sensible defaults
- **Session abandonment** capability

### Breaking Changes
- None (first release)

## Future Plans

- [ ] Webhooks for session completion (instead of polling)
- [ ] Enhanced logging and debugging
- [ ] Request signing (if API support added)
- [ ] Rate limiting helpers
- [ ] Browser SDK
- [ ] Additional language SDKs (Go, Rust, etc.)
