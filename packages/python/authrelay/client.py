"""
AuthRelay client for synchronous authentication requests
"""
import json
import urllib.request
import urllib.error
import warnings
from typing import Optional

from .session import RelaySession
from .types import AuthResult, CreateSessionResponse


class AuthRelay:
    """Client for requesting authentication via AuthRelay"""

    def __init__(
        self,
        api_key: str,
        base_url: str = 'https://authrelay.app',
        timeout: int = 300,
        poll_interval: int = 2000,
    ):
        """
        Initialize AuthRelay client.

        Args:
            api_key: Your AuthRelay API key (required)
            base_url: Base URL for AuthRelay API (default: https://authrelay.app)
            timeout: Default timeout in seconds (default: 300)
            poll_interval: Polling interval in milliseconds (default: 2000)
        """
        if not api_key:
            raise ValueError('AuthRelay: api_key is required')

        self.api_key = api_key
        self.base_url = base_url
        self.timeout = int(timeout * 1000)  # Convert to milliseconds
        self.poll_interval = poll_interval

        # Warn if API key doesn't match expected format (but don't block)
        if not api_key.startswith('ar_'):
            warnings.warn(
                'AuthRelay: API key does not start with "ar_" prefix. '
                'This may indicate an incorrect key format.',
                UserWarning,
            )

    def request_auth(
        self,
        url: str,
        reason: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> AuthResult:
        """
        Request authentication and wait for completion.

        Args:
            url: URL to authenticate against
            reason: Why authentication is needed
            timeout: Override default timeout in seconds

        Returns:
            AuthResult with success, credentials, error, and session_id
        """
        actual_timeout = int((timeout or self.timeout) / 1000)

        try:
            session = self.create_session(url=url, reason=reason)

            credentials = session.wait(timeout=actual_timeout)

            return AuthResult(
                success=True,
                credentials=credentials,
                session_id=session.get_session_id(),
            )
        except TimeoutError:
            return AuthResult(
                success=False,
                error=f'AuthRelay: Session expired. The operator did not complete '
                f'authentication within {actual_timeout} seconds.',
            )
        except Exception as e:
            return AuthResult(
                success=False,
                error=str(e),
            )

    def create_session(
        self,
        url: str,
        reason: Optional[str] = None,
    ) -> RelaySession:
        """
        Create an authentication session without waiting.

        Args:
            url: URL to authenticate against
            reason: Why authentication is needed

        Returns:
            RelaySession object
        """
        try:
            body = json.dumps({
                'url': url,
                'reason': reason or '',
            }).encode('utf-8')

            req = urllib.request.Request(
                f"{self.base_url}/api/sessions",
                method='POST',
                headers={
                    'x-api-key': self.api_key,
                    'Content-Type': 'application/json',
                },
                data=body,
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status != 201 and response.status != 200:
                    raise Exception(
                        f'AuthRelay: Failed to create session: '
                        f'{response.status} {response.reason}'
                    )

                data = json.loads(response.read().decode('utf-8'))

                # Validate response
                if 'session_id' not in data:
                    raise Exception(
                        'AuthRelay: Invalid session response (missing session_id)'
                    )

                return RelaySession(
                    data['session_id'],
                    self.base_url,
                    self.api_key,
                    self.poll_interval,
                    self.timeout,
                )

        except urllib.error.HTTPError as e:
            raise Exception(
                f'AuthRelay: Failed to create session: {e.reason}'
            )
        except json.JSONDecodeError:
            raise Exception('AuthRelay: Invalid JSON response from server')
        except Exception as e:
            if 'AuthRelay' in str(e):
                raise
            raise Exception(f'AuthRelay: Failed to create session: {str(e)}')


class AsyncAuthRelay:
    """Async client for requesting authentication via AuthRelay"""

    def __init__(
        self,
        api_key: str,
        base_url: str = 'https://authrelay.app',
        timeout: int = 300,
        poll_interval: int = 2000,
    ):
        """
        Initialize AsyncAuthRelay client.

        Args:
            api_key: Your AuthRelay API key (required)
            base_url: Base URL for AuthRelay API (default: https://authrelay.app)
            timeout: Default timeout in seconds (default: 300)
            poll_interval: Polling interval in milliseconds (default: 2000)
        """
        if not api_key:
            raise ValueError('AuthRelay: api_key is required')

        self.api_key = api_key
        self.base_url = base_url
        self.timeout = int(timeout * 1000)  # Convert to milliseconds
        self.poll_interval = poll_interval

        # Warn if API key doesn't match expected format (but don't block)
        if not api_key.startswith('ar_'):
            warnings.warn(
                'AuthRelay: API key does not start with "ar_" prefix. '
                'This may indicate an incorrect key format.',
                UserWarning,
            )

    async def request_auth(
        self,
        url: str,
        reason: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> AuthResult:
        """
        Request authentication and wait for completion (async).

        Args:
            url: URL to authenticate against
            reason: Why authentication is needed
            timeout: Override default timeout in seconds

        Returns:
            AuthResult with success, credentials, error, and session_id
        """
        try:
            import aiohttp
        except ImportError:
            raise RuntimeError(
                'AsyncAuthRelay requires aiohttp. '
                'Install with: pip install aiohttp'
            )

        actual_timeout = int((timeout or self.timeout) / 1000)

        try:
            session = await self.create_session(url=url, reason=reason)
            credentials = await session.wait_async(timeout=actual_timeout)

            return AuthResult(
                success=True,
                credentials=credentials,
                session_id=session.get_session_id(),
            )
        except TimeoutError:
            return AuthResult(
                success=False,
                error=f'AuthRelay: Session expired. The operator did not complete '
                f'authentication within {actual_timeout} seconds.',
            )
        except Exception as e:
            return AuthResult(
                success=False,
                error=str(e),
            )

    async def create_session(
        self,
        url: str,
        reason: Optional[str] = None,
    ) -> RelaySession:
        """
        Create an authentication session without waiting (async).

        Args:
            url: URL to authenticate against
            reason: Why authentication is needed

        Returns:
            RelaySession object
        """
        try:
            import aiohttp
        except ImportError:
            raise RuntimeError(
                'AsyncAuthRelay requires aiohttp. '
                'Install with: pip install aiohttp'
            )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/sessions",
                    headers={
                        'x-api-key': self.api_key,
                        'Content-Type': 'application/json',
                    },
                    json={
                        'url': url,
                        'reason': reason or '',
                    },
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status not in (200, 201):
                        raise Exception(
                            f'AuthRelay: Failed to create session: '
                            f'{resp.status} {resp.reason}'
                        )

                    data = await resp.json()

                    # Validate response
                    if 'session_id' not in data:
                        raise Exception(
                            'AuthRelay: Invalid session response (missing session_id)'
                        )

                    return RelaySession(
                        data['session_id'],
                        self.base_url,
                        self.api_key,
                        self.poll_interval,
                        self.timeout,
                    )

        except Exception as e:
            if 'AuthRelay' in str(e):
                raise
            raise Exception(f'AuthRelay: Failed to create session: {str(e)}')
