export type RealtimeEvent = {
  type: string;
  payload: unknown;
};

// Phase 11: intentionally no WebSocket connection.
// Phase 12 will connect this interface to the
// dashboard WebSocket and shared backend event bus.

export function subscribeRealtime(
  _onEvent: (event: RealtimeEvent) => void,
): () => void {
  return () => {
    // No-op unsubscribe until Phase 12.
  };
}