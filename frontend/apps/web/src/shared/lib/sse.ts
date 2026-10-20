export type SseMessageHandler = (event: MessageEvent<string>) => void;

export type RealtimeConnection = {
  close: () => void;
};

/** Browser SSE client (uses same-origin BFF proxy with cookies). */
export function connectSse(
  url: string,
  onMessage: SseMessageHandler,
  onError?: (error: Event) => void,
): RealtimeConnection {
  const source = new EventSource(url, { withCredentials: true });
  source.onmessage = onMessage;
  source.onerror = (ev) => {
    onError?.(ev);
  };
  return {
    close: () => {
      source.close();
    },
  };
}
