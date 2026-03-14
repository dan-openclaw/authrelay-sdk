"""
Session management for AuthRelay
"""
import json
import time
import urllib.request
import urllib.error
from threading import Thread, Event
from typing import Optional, Dict, Any, Callable

from .types import SessionStatus, PollSessionResponse


class RelaySession:
    """Manages a single authentication relay session"""

    def __init__(
        self,
        session_id: str,
        base_url: str,
        api_key: str,
        poll_interval: int = 2000,
        timeout: int = 300_000,
    ):
        self.session_id = session_id
        self.base_url = base_url
        self.api_key = api_key
        self.poll_interval = poll_interval / 1000  # Convert to seconds
        self.timeout = timeout / 1000  # Convert to seconds
        self.status: SessionStatus = 'pending'
        self._stop_event = Event()
        self._completed_event = Event()
        self._credentials: Optional[Dict[str, Any]] = None
        self._error: Optional[Exception] = None
        self._callbacks: Dict[str, list] = {
            'claimed': [],
            'completed': [],
            'expired': [],
            'error': [],
            'statusChanged': [],
        }

    def get_session_id(self) -> str:
        """Get the current session ID"""
        return self.session_id

    def get_status(self) -> SessionStatus:
        """Get the current status"""
        return self.status

    def get_operator_url(self) -> str:
        """Get the operator URL to share with the user"""
        return f"{self.base_url}/session/{self.session_id}"

    def on(self, event: str, callback: Callable) -> None:
        """Register an event listener"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def off(self, event: str, callback: Callable) -> None:
        """Unregister an event listener"""
        if event in self._callbacks and callback in self._callbacks[event]:
            self._callbacks[event].remove(callback)

    def _emit(self, event: str, *args: Any) -> None:
        """Emit an event to all listeners"""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    callback(*args)
                except Exception:
                    pass  # Silently ignore callback errors

    def wait(self, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Wait for the session to complete, expire, or fail.
        
        Args:
            timeout: Override timeout in seconds
            
        Returns:
            Credentials dict if successful, None otherwise
        """
        actual_timeout = timeout if timeout is not None else self.timeout
        
        # Start polling in a background thread
        poll_thread = Thread(target=self._poll_loop)
        poll_thread.daemon = True
        poll_thread.start()

        # Wait for completion or timeout
        if self._completed_event.wait(timeout=actual_timeout):
            if self._error:
                raise self._error
            return self._credentials
        else:
            # Timeout occurred
            self._stop_event.set()
            self.status = 'expired'
            self._emit('expired')
            raise TimeoutError(
                f'AuthRelay: Session expired. The operator did not complete '
                f'authentication within {actual_timeout} seconds.'
            )

    async def wait_async(self, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Async version of wait (requires aiohttp)
        """
        try:
            import asyncio
            from .async_client import AsyncRelaySession
            
            # Delegate to async implementation
            async_session = AsyncRelaySession(
                self.session_id,
                self.base_url,
                self.api_key,
                int(self.poll_interval * 1000),
                int(self.timeout * 1000),
            )
            return await async_session.wait(timeout)
        except ImportError:
            raise RuntimeError(
                'Async support requires aiohttp. Install with: pip install aiohttp'
            )

    def abandon(self) -> None:
        """Abandon the session"""
        self._stop_event.set()
        self.status = 'failed'

        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/sessions/{self.session_id}/abandon",
                method='POST',
                headers={
                    'x-api-key': self.api_key,
                    'Content-Type': 'application/json',
                    'User-Agent': 'AuthRelay-Python-SDK/1.0.0',
                },
                data=b'',
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status not in (200, 204):
                    raise Exception(f'Failed to abandon session: {response.status}')
        except urllib.error.HTTPError as e:
            raise Exception(f'Failed to abandon session: {e.reason}')
        except Exception as e:
            raise Exception(f'Failed to abandon session: {str(e)}')

    def _poll_loop(self) -> None:
        """Main polling loop (runs in background thread)"""
        backoff_ms = 2000
        max_backoff_ms = 5000
        start_time = time.time()

        while not self._stop_event.is_set():
            # Check if we've exceeded the session timeout
            elapsed = (time.time() - start_time) * 1000
            if elapsed > self.timeout * 1000:
                self.status = 'expired'
                self._emit('expired')
                self._completed_event.set()
                return

            try:
                # Poll the session status
                req = urllib.request.Request(
                    f"{self.base_url}/api/sessions/{self.session_id}",
                    method='GET',
                    headers={'x-api-key': self.api_key, 'User-Agent': 'AuthRelay-Python-SDK/1.0.0'},
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status != 200:
                        raise Exception(f'Failed to poll session: {response.status}')

                    data = json.loads(response.read().decode('utf-8'))
                    prev_status = self.status
                    self.status = data['status']

                    # Emit status changed event
                    if prev_status != self.status:
                        self._emit('statusChanged', self.status)

                    if self.status == 'claimed':
                        if prev_status != 'claimed':
                            self._emit('claimed')
                        # Continue polling with backoff
                        time.sleep(backoff_ms / 1000)
                        backoff_ms = min(backoff_ms + 1000, max_backoff_ms)

                    elif self.status == 'completed':
                        if 'credentials' in data and data['credentials']:
                            self._credentials = data['credentials']
                            self._emit('completed', self._credentials)
                        else:
                            self._error = Exception(
                                'AuthRelay: Session completed but no credentials returned'
                            )
                            self._emit('error', self._error)
                        self._completed_event.set()
                        return

                    elif self.status == 'expired':
                        self._emit('expired')
                        self._completed_event.set()
                        return

                    elif self.status == 'failed':
                        error_msg = data.get('error', 'Unknown error')
                        self._error = Exception(f'AuthRelay: Session failed: {error_msg}')
                        self._emit('error', self._error)
                        self._completed_event.set()
                        return

                    elif self.status == 'pending':
                        # Continue polling with backoff
                        time.sleep(backoff_ms / 1000)
                        backoff_ms = min(backoff_ms + 1000, max_backoff_ms)

            except urllib.error.HTTPError as e:
                self._error = Exception(f'AuthRelay: Failed to poll session: {e.reason}')
                self._emit('error', self._error)
                self._completed_event.set()
                return
            except Exception as e:
                self._error = Exception(f'AuthRelay: Polling error: {str(e)}')
                self._emit('error', self._error)
                self._completed_event.set()
                return
