"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

import { connectSse } from "@/shared/lib/sse";

type RealtimePayload = {
  type: string;
  tenant_id?: string;
  query_key?: unknown[];
};

/** Subscribes to SSE and patches TanStack Query cache when events include query_key. */
export function useRealtime(enabled = true) {
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!enabled) {
      return;
    }
    const conn = connectSse("/api/bff/api/v1/realtime/stream", (event) => {
      try {
        const payload = JSON.parse(event.data) as RealtimePayload;
        if (payload.query_key) {
          void queryClient.invalidateQueries({ queryKey: payload.query_key as readonly unknown[] });
        }
      } catch {
        // ignore malformed events
      }
    });
    return () => conn.close();
  }, [enabled, queryClient]);
}
