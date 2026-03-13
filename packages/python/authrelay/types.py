"""
Type definitions for AuthRelay SDK
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Literal

SessionStatus = Literal['pending', 'claimed', 'completed', 'expired', 'failed']


@dataclass
class AuthResult:
    """Result of an authentication request"""
    success: bool
    credentials: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class CreateSessionResponse:
    """Server response when creating a session"""
    session_id: str
    status: SessionStatus
    session_token: str
    expires_at: str
    operator_url: str
    poll_url: str


@dataclass
class PollSessionResponse:
    """Server response when polling session status"""
    id: str
    status: SessionStatus
    createdAt: str
    claimedAt: Optional[str] = None
    completedAt: Optional[str] = None
    expiresAt: Optional[str] = None
    error: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
