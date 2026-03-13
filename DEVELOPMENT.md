# Development Guide

## Building the SDKs

### TypeScript SDK

#### Prerequisites
- Node.js 18+
- npm or yarn

#### Build

```bash
cd packages/typescript
npm install
npm run build
```

This produces:
- `dist/index.js` — CommonJS
- `dist/index.mjs` — ES Module
- `dist/*.d.ts` — Type definitions

#### Test

```bash
API_KEY=ar_live_... npm run build && npx ts-node test/integration.ts
```

#### Publish to npm

```bash
cd packages/typescript
npm publish
```

### Python SDK

#### Prerequisites
- Python 3.8+
- pip

#### Build

```bash
cd packages/python

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
```

#### Test

```bash
API_KEY=ar_live_... python test_authrelay.py
```

#### Publish to PyPI

```bash
cd packages/python
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
```

## Key Implementation Details

### Polling Strategy

Both SDKs implement exponential backoff:
- Start: 2000ms
- Increment: +1000ms per attempt
- Cap: 5000ms

This is non-configurable and hardcoded in:
- **TypeScript**: `packages/typescript/src/session.ts` (line ~140)
- **Python**: `packages/python/authrelay/session.py` (line ~180)

### Zero-Dependency Sync Clients

- **TypeScript**: Uses native `fetch` (available in Node.js 18+)
- **Python**: Uses `urllib.request` from the standard library

No external dependencies for synchronous use.

### Async Implementation

- **TypeScript**: Native async/await with EventEmitter
- **Python**: 
  - Sync: Threading-based polling
  - Async: Optional `aiohttp` dependency for async HTTP

### Error Messages

All error messages follow the pattern:
```
AuthRelay: [error description]
```

Example: `"AuthRelay: Session expired. The operator did not complete authentication within 300 seconds."`

### API Key Validation

Both SDKs:
1. Validate that `apiKey` is provided (throw error if missing)
2. Warn if key doesn't start with `ar_` (but don't block)

### Session Lifecycle

1. **Create**: POST to `/api/sessions`
2. **Poll**: GET `/api/sessions/:id` with exponential backoff
3. **Complete**: Status transitions to `completed`, credentials returned once
4. **Cleanup**: Remove event listeners, clear timeouts, abandon if needed

### Testing

For testing without a real API:
- Use mock/stub implementations
- Both SDKs accept configurable `baseUrl` for testing against mocks

## Directory Structure

```
authrelay-sdk/
├── LICENSE
├── README.md
├── DEVELOPMENT.md              ← You are here
├── .gitignore
├── packages/
│   ├── typescript/
│   │   ├── src/
│   │   │   ├── index.ts        (exports)
│   │   │   ├── client.ts       (AuthRelay class)
│   │   │   ├── session.ts      (RelaySession class)
│   │   │   └── types.ts        (type definitions)
│   │   ├── test/
│   │   │   ├── test.js         (basic test)
│   │   │   └── integration.ts  (real API test)
│   │   ├── scripts/
│   │   │   └── build-esm.js    (ESM/CJS build helper)
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── .npmignore
│   │   └── README.md
│   └── python/
│       ├── authrelay/
│       │   ├── __init__.py      (package exports)
│       │   ├── client.py        (AuthRelay + AsyncAuthRelay)
│       │   ├── session.py       (RelaySession)
│       │   └── types.py         (dataclasses)
│       ├── test_authrelay.py    (real API test)
│       ├── setup.py
│       ├── pyproject.toml
│       └── README.md
```

## Important Files to Review

### Type/API Contract
- **TypeScript**: `packages/typescript/src/types.ts`
- **Python**: `packages/python/authrelay/types.py`

### Client Implementation
- **TypeScript**: `packages/typescript/src/client.ts`
- **Python**: `packages/python/authrelay/client.py`

### Session State Management
- **TypeScript**: `packages/typescript/src/session.ts`
- **Python**: `packages/python/authrelay/session.py`

## Debugging

### TypeScript
```bash
cd packages/typescript
npm run build
node -e "const { AuthRelay } = require('./dist'); console.log(new AuthRelay({ apiKey: 'test' }))"
```

### Python
```bash
cd packages/python
python -c "from authrelay import AuthRelay; print(AuthRelay(api_key='test'))"
```

## Common Issues

### TypeScript Build Fails
- Ensure TypeScript is installed: `npm install`
- Check Node.js version >= 18
- Clear cache: `rm -rf dist/ node_modules/ && npm install`

### Python Import Error
- Ensure you're in the right directory
- Install in dev mode: `pip install -e .`
- Check Python version >= 3.8: `python --version`

### Async Test Fails
- Python: Install aiohttp with `pip install aiohttp`
- TypeScript: Ensure Node.js >= 18

## Future Enhancements

- [ ] Add request/response logging
- [ ] Implement retry logic for failed requests
- [ ] Add request signing (if API requires)
- [ ] Support for webhook callbacks (instead of polling)
- [ ] Connection pooling for multiple sessions
- [ ] Rate limiting helpers
