# AuthRelay Agent SDK

A dual-language SDK for AI agents to request human-in-the-loop authentication via the AuthRelay API.

## Packages

- **[TypeScript](./packages/typescript/)** (`authrelay`) — npm package for Node.js and browser environments
- **[Python](./packages/python/)** (`authrelay`) — pip package for Python 3.8+

## Quick Start

### TypeScript

```bash
npm install authrelay
```

```typescript
import { AuthRelay } from 'authrelay';

const relay = new AuthRelay({ apiKey: 'ar_live_...' });

const result = await relay.requestAuth({
  url: 'https://example.com/login',
  reason: 'Need to log in to access dashboard',
  timeout: 300_000, // 5 minutes
});

if (result.success) {
  console.log('Got credentials:', result.credentials);
} else {
  console.error('Auth failed:', result.error);
}
```

### Python

```bash
pip install authrelay
```

```python
from authrelay import AuthRelay

relay = AuthRelay(api_key="ar_live_...")

result = relay.request_auth(
    url="https://example.com/login",
    reason="Need to log in to access dashboard",
    timeout=300,
)

if result.success:
    print("Got credentials:", result.credentials)
else:
    print("Auth failed:", result.error)
```

## Features

- ✅ **Zero dependencies** (for sync clients)
- ✅ **Exponential backoff polling** (2s → 3s → 5s → 5s cap)
- ✅ **Event-driven architecture** (TypeScript)
- ✅ **Async support** (both TypeScript and Python)
- ✅ **Full type safety** (TypeScript)
- ✅ **Configurable base URL** (for self-hosted instances)
- ✅ **Helpful error messages**

## Documentation

- [TypeScript SDK Documentation](./packages/typescript/README.md)
- [Python SDK Documentation](./packages/python/README.md)

## API Reference

See the AuthRelay API documentation at https://authrelay.app

## License

MIT
