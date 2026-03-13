import { EventEmitter } from 'events';
import { SessionStatus, PollSessionResponse, SessionEvents } from './types';

/**
 * Manages a single authentication relay session
 */
export class RelaySession extends EventEmitter {
  private sessionId: string;
  private status: SessionStatus = 'pending';
  private baseUrl: string;
  private apiKey: string;
  private pollInterval: number;
  private timeout: number;
  private pollTimeoutHandle?: NodeJS.Timeout;
  private sessionTimeoutHandle?: NodeJS.Timeout;

  constructor(
    sessionId: string,
    baseUrl: string,
    apiKey: string,
    pollInterval: number,
    timeout: number,
  ) {
    super();
    this.sessionId = sessionId;
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
    this.pollInterval = pollInterval;
    this.timeout = timeout;
  }

  /**
   * Get the current session ID
   */
  getSessionId(): string {
    return this.sessionId;
  }

  /**
   * Get the current status
   */
  getStatus(): SessionStatus {
    return this.status;
  }

  /**
   * Get the operator URL to share with the user
   */
  getOperatorUrl(): string {
    return `${this.baseUrl}/session/${this.sessionId}`;
  }

  /**
   * Wait for the session to complete, expire, or fail
   */
  async wait(): Promise<Record<string, unknown> | null> {
    return new Promise((resolve, reject) => {
      // Set up session timeout
      this.sessionTimeoutHandle = setTimeout(() => {
        this.status = 'expired';
        this.emit('expired');
        this.stopPolling();
        reject(
          new Error(
            'AuthRelay: Session expired. The operator did not complete authentication within ' +
            `${this.timeout / 1000} seconds.`,
          ),
        );
      }, this.timeout);

      // Set up event handlers
      const onCompleted = (credentials: Record<string, unknown>) => {
        this.cleanup();
        resolve(credentials);
      };

      const onError = (error: Error) => {
        this.cleanup();
        reject(error);
      };

      const onExpired = () => {
        this.cleanup();
        reject(
          new Error(
            'AuthRelay: Session expired. The operator did not complete authentication within ' +
            `${this.timeout / 1000} seconds.`,
          ),
        );
      };

      this.once('completed', onCompleted);
      this.once('error', onError);
      this.once('expired', onExpired);

      // Start polling
      this.startPolling();
    });
  }

  /**
   * Abandon the session
   */
  async abandon(): Promise<void> {
    this.status = 'failed';
    this.stopPolling();
    this.cleanup();

    const response = await fetch(`${this.baseUrl}/api/sessions/${this.sessionId}/abandon`, {
      method: 'POST',
      headers: {
        'x-api-key': this.apiKey,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to abandon session: ${response.statusText}`);
    }
  }

  /**
   * Start polling the session status
   */
  private startPolling(): void {
    let backoffMs = 2000;
    const maxBackoffMs = 5000;

    const poll = async () => {
      try {
        const response = await fetch(`${this.baseUrl}/api/sessions/${this.sessionId}`, {
          method: 'GET',
          headers: {
            'x-api-key': this.apiKey,
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to poll session: ${response.statusText}`);
        }

        const data = (await response.json()) as PollSessionResponse;
        const previousStatus = this.status;
        this.status = data.status;

        // Emit status changed event
        if (previousStatus !== this.status) {
          this.emit('statusChanged', this.status);
        }

        switch (data.status) {
          case 'claimed':
            if (previousStatus !== 'claimed') {
              this.emit('claimed');
            }
            // Continue polling
            this.pollTimeoutHandle = setTimeout(poll, backoffMs);
            backoffMs = Math.min(backoffMs + 1000, maxBackoffMs);
            break;

          case 'completed':
            if (data.credentials) {
              this.emit('completed', data.credentials);
            } else {
              this.emit('error', new Error('AuthRelay: Session completed but no credentials returned'));
            }
            this.stopPolling();
            break;

          case 'expired':
            this.emit('expired');
            this.stopPolling();
            break;

          case 'failed':
            this.emit('error', new Error(`AuthRelay: Session failed: ${data.error || 'Unknown error'}`));
            this.stopPolling();
            break;

          case 'pending':
            // Continue polling
            this.pollTimeoutHandle = setTimeout(poll, backoffMs);
            backoffMs = Math.min(backoffMs + 1000, maxBackoffMs);
            break;
        }
      } catch (error) {
        this.emit('error', error instanceof Error ? error : new Error(String(error)));
        this.stopPolling();
      }
    };

    // Initial poll
    this.pollTimeoutHandle = setTimeout(poll, 0);
  }

  /**
   * Stop polling
   */
  private stopPolling(): void {
    if (this.pollTimeoutHandle) {
      clearTimeout(this.pollTimeoutHandle);
      this.pollTimeoutHandle = undefined;
    }
  }

  /**
   * Cleanup resources
   */
  private cleanup(): void {
    this.stopPolling();
    if (this.sessionTimeoutHandle) {
      clearTimeout(this.sessionTimeoutHandle);
      this.sessionTimeoutHandle = undefined;
    }
    this.removeAllListeners();
  }
}
