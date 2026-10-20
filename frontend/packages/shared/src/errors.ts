import { z } from "zod";

export const errorEnvelopeSchema = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.record(z.unknown()).optional().default({}),
    trace_id: z.string(),
  }),
});

export type ErrorEnvelope = z.infer<typeof errorEnvelopeSchema>;

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly details: Record<string, unknown>;
  readonly traceId: string;

  constructor(
    message: string,
    opts: { code: string; status: number; details?: Record<string, unknown>; traceId: string },
  ) {
    super(message);
    this.name = "ApiError";
    this.code = opts.code;
    this.status = opts.status;
    this.details = opts.details ?? {};
    this.traceId = opts.traceId;
  }
}

export function parseApiError(status: number, body: unknown): ApiError {
  const parsed = errorEnvelopeSchema.safeParse(body);
  if (parsed.success) {
    const e = parsed.data.error;
    return new ApiError(e.message, {
      code: e.code,
      status,
      details: e.details ?? {},
      traceId: e.trace_id,
    });
  }
  return new ApiError("Request failed", {
    code: "common.unknown",
    status,
    details: {},
    traceId: "unknown",
  });
}
