# AuthRelay SDK for Python

Python SDK for requesting human-in-the-loop authentication via AuthRelay.

## Installation

### Sync Only

```bash
pip install authrelay
```

### With Async Support

```bash
pip install authrelay[async]
```

## Quick Start

### Synchronous

```python
from authrelay import AuthRelay

relay = AuthRelay(api_key='ar_live_...')

result = relay.request_auth(
    url='https://dashboard.example.com/login',
    reason='Need access to analytics dashboard',
    timeout=300,  # seconds
)

if result.success:
    print('Cookies:', result.credentials.get('cookies'))
    print('Session token:', result.credentials.get('sessionToken'))
else:
    print('Auth failed:', result.error)
```

### Asynchronous

```python
import asyncio
from authrelay import AsyncAuthRelay

async def main():
    relay = AsyncAuthRelay(api_key='ar_live_...')
    
    result = await relay.request_auth(
        url='https://dashboard.example.com/login',
        reason='Need access to analytics dashboard',
        timeout=300,
    )
    
    if result.success:
        print('Credentials:', result.credentials)
    else:
        print('Auth failed:', result.error)

asyncio.run(main())
```

## API Reference

### AuthRelay Constructor

```python
relay = AuthRelay(
    api_key='ar_live_...',      # Required: your AuthRelay API key
    base_url='https://authrelay.app',  # Optional: API base URL
    timeout=300,                # Optional: default timeout in seconds
    poll_interval=2000,         # Optional: polling interval in ms
)
```

### request_auth()

Convenience method that creates a session and waits for completion.

```python
result = relay.request_auth(
    url='https://example.com/login',  # Required
    reason='Why you need auth',       # Optional
    timeout=300,                      # Optional: override timeout
)
```

Returns `AuthResult`:
```python
@dataclass
class AuthResult:
    success: bool
    credentials: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    session_id: Optional[str] = None
```

### create_session()

Create a session without waiting for completion.

```python
session = relay.create_session(
    url='https://example.com/login',
    reason='Why you need auth',
)
```

Returns a `RelaySession` object.

## RelaySession

### Methods

```python
# Get the session ID
session.get_session_id() -> str

# Get the current status
session.get_status() -> str

# Get the operator URL to share with the user
session.get_operator_url() -> str

# Wait for completion (blocks until done)
credentials = session.wait(timeout=300)

# Abandon the session
session.abandon()

# Register event handlers
session.on('claimed', lambda: print('Operator picked it up!'))
session.on('completed', lambda creds: print('Got credentials:', creds))
session.on('expired', lambda: print('Session expired'))
session.on('error', lambda err: print('Error:', err))
```

### Example

```python
from authrelay import AuthRelay

relay = AuthRelay(api_key='ar_live_...')

session = relay.create_session(
    url='https://example.com/login',
    reason='Login needed',
)

# Share the operator URL with the user
print('Open this link to authenticate:', session.get_operator_url())

# Register event handlers
session.on('claimed', lambda: print('Operator picked it up!'))
session.on('completed', lambda creds: print('Got credentials:', creds))
session.on('expired', lambda: print('Timed out'))
session.on('error', lambda err: print('Error:', err))

try:
    credentials = session.wait(timeout=300)
    print('Authentication completed:', credentials)
except Exception as error:
    print('Authentication failed:', error)
```

## Error Handling

```python
from authrelay import AuthRelay

relay = AuthRelay(api_key='ar_live_...')

try:
    result = relay.request_auth(
        url='https://example.com/login',
    )
    
    if not result.success:
        # Handle auth failure
        print(f'Auth failed: {result.error}')
    else:
        # Use credentials
        print('Got credentials:', result.credentials)
except Exception as error:
    # Handle validation or network errors
    print(f'Error: {error}')
```

Common error messages:

- `"AuthRelay: Session expired..."` — operator didn't complete within timeout
- `"AuthRelay: Failed to create session..."` — API key invalid or API unavailable
- `"AuthRelay: Session failed: ..."` — operator encountered an error

## Polling & Backoff

The SDK uses exponential backoff when polling:
- Starts at 2 seconds
- Increases by 1 second each attempt
- Caps at 5 seconds

This is automatic and cannot be overridden per-request.

## Configuration for Self-Hosted

To use a self-hosted AuthRelay instance:

```python
relay = AuthRelay(
    api_key='ar_live_...',
    base_url='https://authrelay.your-domain.com',
)
```

## Credentials Format

The credentials object returned from AuthRelay may include:

```python
{
    'cookies': {                    # HTTP cookies
        'session_id': 'abc123',
        ...
    },
    'sessionToken': 'bearer_token', # Session/bearer token
    ...                             # Additional fields
}
```

The exact format depends on the target website and how the operator authenticated.

## Threading & Async

- **`request_auth()`** — blocks the current thread
- **`create_session()` + `session.wait()`** — blocks the current thread; run in a thread pool if needed
- **`AsyncAuthRelay`** — use in `async` contexts for non-blocking I/O

For running synchronous requests concurrently:

```python
from concurrent.futures import ThreadPoolExecutor
from authrelay import AuthRelay

relay = AuthRelay(api_key='ar_live_...')

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(
            relay.request_auth,
            url=f'https://app{i}.example.com/login',
        )
        for i in range(5)
    ]
    
    results = [f.result() for f in futures]
```

## License

MIT
