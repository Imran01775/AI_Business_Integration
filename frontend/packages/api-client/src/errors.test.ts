import { describe, expect, it } from "vitest";

import { parseApiError } from "./errors";

describe("parseApiError", () => {
  it("maps standard error envelope", () => {
    const err = parseApiError(401, {
      error: {
        code: "auth.unauthenticated",
        message: "Not signed in",
        details: {},
        trace_id: "trace-1",
      },
    });
    expect(err.code).toBe("auth.unauthenticated");
    expect(err.status).toBe(401);
    expect(err.traceId).toBe("trace-1");
  });

  it("falls back for unknown body", () => {
    const err = parseApiError(500, { foo: "bar" });
    expect(err.code).toBe("common.unknown");
  });
});
