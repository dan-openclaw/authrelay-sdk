import { SessionStatus, PollSessionResponse } from './types';

type EventHandler = (...args: any[]) => void;

/**
 * Manages a single authentication relay session
 */
export class RelaySession {
  private sessionId: string;
  private status: SessionStatus = 'pending';
  private baseUrl: string;
  private apiKey: string;
  private pollInterval: number;
  private timeout: number;
  private pollTimeoutHandle?: ReturnType<typeof setTimeout>;
  private sessionTimeoutHandle?: ReturnType<typeof setTimeout>;
  private listeners: Map<string, EventHandler[]> = new Map();

  constructor(
    sessionId: string,
    baseUrl: string,
    apiKey: string,
    pollInterval: number,
    timeout: number,
  ) {
    this.sessionId = sessionId;
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
    this.pollInterval = pollInterval;
    this.timeout = timeout;
  }

  /** Register an event handler */
  on(event: string, handler: EventHandler): this {
    if (!this.listeners.has(event)) this.listeners.set(event, []);
    this.listeners.get(event)!.push(handler);
    return this;
  }

  /** Register a one-time event handler */
  once(event: string, handler: EventHandler): this {
    const wrapped = (...args: any[]) => {
      this.off(event, wrapped);
      handler(...args);
    };
    return this.on(event, wrapped);
  }

  /** Remove an event handler */
  off(event: string, handler: EventHandler): this {
    const handlers = this.listeners.get(event);
    if (handlers) {
      this.listeners.set(event, handlers.filter(h => h !== handler));
    }
    return this;
  }

  /** Emit an event */
  private emit(event: string, ...args: any[]): void {
    const handlers = this.listeners.get(event);
    if (handlers) {
      for (const handler of [...handlers]) {
        handler(...args);
      }
    }
  }

  /** Remove all listeners */
  private removeAllListeners(): void {
    this.listeners.clear();
  }

  /** Get the current session ID */
  getSessionId(): string {
    return this.sessionId;
  }

  /** Get the current status */
  getStatus(): SessionStatus {
    return this.status;
  }

  /** Get the operator URL to share with the user */
  getOperatorUrl(): string {
    return `${this.baseUrl}/session/${this.sessionId}`;
  }

  /** Wait for the session to complete, expire, or fail */
  async wait(): Promise<Record<string, unknown> | null> {
    return new Promise((resolve, reject) => {
      this.sessionTimeoutHandle = setTimeout(() => {
        this.status = 'expired';
        this.emit('expired');
        this.stopPolling();
        reject(
          new Error(
            `AuthRelay: Session expired. The operator did not complete authentication within ${this.timeout / 1000} seconds.`,
          ),
        );
      }, this.timeout);

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
            `AuthRelay: Session expired. The operator did not complete authentication within ${this.timeout / 1000} seconds.`,
          ),
        );
      };

      this.once('completed', onCompleted);
      this.once('error', onError);
      this.once('expired', onExpired);

      this.startPolling();
    });
  }

  /** Abandon the session */
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

  private startPolling(): void {
    let backoffMs = 2000;
    const maxBackoffMs = 5000;

    const poll = async () => {
      try {
        const response = await fetch(`${this.baseUrl}/api/sessions/${this.sessionId}`, {
          method: 'GET',
          headers: { 'x-api-key': this.apiKey },
        });

        if (!response.ok) {
          throw new Error(`Failed to poll session: ${response.statusText}`);
        }

        const data = (await response.json()) as PollSessionResponse;
        const previousStatus = this.status;
        this.status = data.status;

        if (previousStatus !== this.status) {
          this.emit('statusChanged', this.status);
        }

        switch (data.status) {
          case 'claimed':
            if (previousStatus !== 'claimed') this.emit('claimed');
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
            this.pollTimeoutHandle = setTimeout(poll, backoffMs);
            backoffMs = Math.min(backoffMs + 1000, maxBackoffMs);
            break;
        }
      } catch (error) {
        this.emit('error', error instanceof Error ? error : new Error(String(error)));
        this.stopPolling();
      }
    };

    this.pollTimeoutHandle = setTimeout(poll, 0);
  }

  private stopPolling(): void {
    if (this.pollTimeoutHandle) {
      clearTimeout(this.pollTimeoutHandle);
      this.pollTimeoutHandle = undefined;
    }
  }

  private cleanup(): void {
    this.stopPolling();
    if (this.sessionTimeoutHandle) {
      clearTimeout(this.sessionTimeoutHandle);
      this.sessionTimeoutHandle = undefined;
    }
    this.removeAllListeners();
  }
}
