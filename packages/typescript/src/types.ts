/**
 * Result of an authentication request
 */
export interface AuthResult {
  success: boolean;
  credentials?: {
    cookies?: Record<string, string>;
    sessionToken?: string;
    [key: string]: unknown;
  };
  error?: string;
  sessionId?: string;
}

/**
 * Session status
 */
export type SessionStatus = 'pending' | 'claimed' | 'completed' | 'expired' | 'failed';

/**
 * Server response when creating a session
 */
export interface CreateSessionResponse {
  session_id: string;
  status: SessionStatus;
  session_token: string;
  expires_at: string;
  operator_url: string;
  poll_url: string;
}

/**
 * Server response when polling session status
 */
export interface PollSessionResponse {
  id: string;
  status: SessionStatus;
  createdAt: string;
  claimedAt?: string;
  completedAt?: string;
  expiresAt: string;
  error?: string;
  credentials?: Record<string, unknown>;
}

/**
 * Options for creating an AuthRelay instance
 */
export interface AuthRelayOptions {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
  pollInterval?: number;
}

/**
 * Options for requesting authentication
 */
export interface RequestAuthOptions {
  url: string;
  reason?: string;
  timeout?: number;
}

/**
 * Options for creating a session
 */
export interface CreateSessionOptions {
  url: string;
  reason?: string;
}

/**
 * Events emitted by RelaySession
 */
export interface SessionEvents {
  claimed: () => void;
  completed: (credentials: Record<string, unknown>) => void;
  expired: () => void;
  error: (error: Error) => void;
  statusChanged: (status: SessionStatus) => void;
}
