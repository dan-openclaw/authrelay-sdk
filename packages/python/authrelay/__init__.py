"""
AuthRelay SDK for Python
"""
from .client import AuthRelay, AsyncAuthRelay
from .session import RelaySession
from .types import AuthResult, SessionStatus

__version__ = '1.0.0'
__all__ = [
    'AuthRelay',
    'AsyncAuthRelay',
    'RelaySession',
    'AuthResult',
    'SessionStatus',
]
