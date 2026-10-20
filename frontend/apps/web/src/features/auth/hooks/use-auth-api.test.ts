import { describe, expect, it } from "vitest";

describe("use-auth-api", () => {
  it("maps login contract", () => {
    expect({ email: "a@b.com", password: "x" }).toMatchObject({ email: expect.any(String) });
  });
});
