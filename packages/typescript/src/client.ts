import { RelaySession } from './session';
import {
  AuthRelayOptions,
  RequestAuthOptions,
  CreateSessionOptions,
  CreateSessionResponse,
  AuthResult,
} from './types';

/**
 * Client for requesting authentication via AuthRelay
 */
export class AuthRelay {
  private apiKey: string;
  private baseUrl: string;
  private timeout: number;
  private pollInterval: number;

  constructor(options: AuthRelayOptions) {
    if (!options.apiKey) {
      throw new Error('AuthRelay: apiKey is required');
    }

    this.apiKey = options.apiKey;
    this.baseUrl = options.baseUrl || 'https://authrelay.app';
    this.timeout = options.timeout || 300_000; // 5 minutes default
    this.pollInterval = options.pollInterval || 2000;

    // Warn if API key doesn't match expected format (but don't block)
    if (!options.apiKey.startsWith('ar_')) {
      console.warn(
        'AuthRelay: API key does not start with "ar_" prefix. This may indicate an incorrect key format.',
      );
    }
  }

  /**
   * Request authentication and wait for completion
   */
  async requestAuth(options: RequestAuthOptions): Promise<AuthResult> {
    const timeout = options.timeout || this.timeout;

    try {
      const session = await this.createSession({
        url: options.url,
        reason: options.reason,
      });

      const credentials = await Promise.race([
        session.wait(),
        new Promise<null>((_, reject) =>
          setTimeout(
            () => reject(new Error('AuthRelay: Authentication timeout')),
            timeout,
          ),
        ),
      ]);

      return {
        success: true,
        credentials: credentials as Record<string, unknown>,
        sessionId: session.getSessionId(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  /**
   * Create an authentication session without waiting
   */
  async createSession(options: CreateSessionOptions): Promise<RelaySession> {
    const response = await fetch(`${this.baseUrl}/api/sessions`, {
      method: 'POST',
      headers: {
        'x-api-key': this.apiKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: options.url,
        reason: options.reason || '',
      }),
    });

    if (!response.ok) {
      throw new Error(
        `AuthRelay: Failed to create session: ${response.status} ${response.statusText}`,
      );
    }

    const data = (await response.json()) as CreateSessionResponse;

    // Validate response
    if (!data.session_id) {
      throw new Error('AuthRelay: Invalid session response (missing session_id)');
    }

    return new RelaySession(
      data.session_id,
      this.baseUrl,
      this.apiKey,
      this.pollInterval,
      this.timeout,
    );
  }
}
