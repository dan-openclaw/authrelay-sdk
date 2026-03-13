# AuthRelay SDK for TypeScript

TypeScript SDK for requesting human-in-the-loop authentication via AuthRelay.

## Installation

```bash
npm install authrelay
```

## Quick Start

```typescript
import { AuthRelay } from 'authrelay';

const relay = new AuthRelay({ apiKey: 'ar_live_...' });

const result = await relay.requestAuth({
  url: 'https://dashboard.example.com/login',
  reason: 'Need access to analytics dashboard',
  timeout: 300_000, // 5 minutes
});

if (result.success) {
  console.log('Cookies:', result.credentials?.cookies);
  console.log('Session token:', result.credentials?.sessionToken);
} else {
  console.error('Auth failed:', result.error);
}
```

## API Reference

### AuthRelay Constructor

```typescript
const relay = new AuthRelay({
  apiKey: string;           // Required: your AuthRelay API key
  baseUrl?: string;         // Default: 'https://authrelay.app'
  timeout?: number;         // Default: 300_000 (5 minutes)
  pollInterval?: number;    // Default: 2000 (ms)
});
```

### requestAuth()

Convenience method that creates a session and waits for completion.

```typescript
const result = await relay.requestAuth({
  url: string;              // Required: URL to authenticate against
  reason?: string;          // Optional: why authentication is needed
  timeout?: number;         // Optional: override default timeout
});
```

Returns `AuthResult`:
```typescript
{
  success: boolean;
  credentials?: {
    cookies?: Record<string, string>;
    sessionToken?: string;
    [key: string]: unknown;
  };
  error?: string;
  sessionId?: string;
}
```

### createSession()

Create a session without waiting for completion.

```typescript
const session = await relay.createSession({
  url: string;              // Required: URL to authenticate against
  reason?: string;          // Optional: why authentication is needed
});
```

Returns a `RelaySession` object.

## RelaySession

### Events

The `RelaySession` extends EventEmitter and emits the following events:

- **`claimed`** — An operator has claimed the session
- **`completed(credentials)`** — Authentication completed successfully
- **`expired`** — Session expired without completion
- **`error(error)`** — An error occurred
- **`statusChanged(status)`** — Session status changed

### Methods

```typescript
// Get the session ID
session.getSessionId(): string

// Get the current status
session.getStatus(): SessionStatus

// Get the operator URL to share with the user
session.getOperatorUrl(): string

// Wait for completion (resolves with credentials or rejects)
await session.wait(): Promise<Record<string, unknown>>

// Abandon the session
await session.abandon(): Promise<void>
```

### Example

```typescript
import { AuthRelay } from 'authrelay';

const relay = new AuthRelay({ apiKey: 'ar_live_...' });

const session = await relay.createSession({
  url: 'https://example.com/login',
  reason: 'Login needed',
});

// Share the operator URL with the user
console.log('Open this link to authenticate:', session.getOperatorUrl());

session.on('claimed', () => console.log('Operator picked it up!'));
session.on('completed', (creds) => console.log('Got credentials:', creds));
session.on('expired', () => console.log('Timed out'));
session.on('error', (err) => console.error('Error:', err));

try {
  const credentials = await session.wait();
  console.log('Authentication completed:', credentials);
} catch (error) {
  console.error('Authentication failed:', error);
}
```

## Error Handling

All errors are properly typed. Common errors:

```typescript
try {
  const result = await relay.requestAuth({
    url: 'https://example.com/login',
  });
  
  if (!result.success) {
    // Handle auth failure
    console.error(`Auth failed: ${result.error}`);
  }
} catch (error) {
  // Handle network or validation errors
  if (error instanceof Error) {
    console.error(`Fatal error: ${error.message}`);
  }
}
```

Common error messages:

- `"AuthRelay: Session expired..."` — operator didn't complete within timeout
- `"AuthRelay: Failed to create session..."` — API key invalid or API unavailable
- `"AuthRelay: Authentication timeout"` — timeout was reached

## Polling & Backoff

The SDK uses exponential backoff when polling:
- Starts at 2 seconds
- Increases by 1 second each attempt
- Caps at 5 seconds

This is automatic and cannot be overridden per-request.

## Configuration for Self-Hosted

To use a self-hosted AuthRelay instance:

```typescript
const relay = new AuthRelay({
  apiKey: 'ar_live_...',
  baseUrl: 'https://authrelay.your-domain.com',
});
```

## Credentials Format

The credentials object returned from AuthRelay may include:

```typescript
{
  cookies?: Record<string, string>;      // HTTP cookies
  sessionToken?: string;                 // Session token/bearer token
  [key: string]: unknown;                // Additional fields from server
}
```

The exact format depends on the target website and how the operator authenticated.

## License

MIT
