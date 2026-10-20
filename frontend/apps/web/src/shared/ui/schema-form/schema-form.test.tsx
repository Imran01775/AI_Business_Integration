import { render, screen } from "@testing-library/react";
import { axe } from "vitest-axe";
import "vitest-axe/extend-expect";
import { describe, expect, it, vi } from "vitest";

import { SchemaForm } from "./schema-form";

describe("SchemaForm", () => {
  it("renders bool and str fields", () => {
    render(
      <SchemaForm
        schema={{
          "user.locale": { type: "str", enum: ["en", "bn"] },
          "user.notifications.email": { type: "bool" },
        }}
        values={{ "user.locale": "en", "user.notifications.email": true }}
        saveLabel="Save"
        onSubmit={vi.fn()}
      />,
    );
    expect(screen.getByText("user.locale")).toBeInTheDocument();
    expect(screen.getByText("user.notifications.email")).toBeInTheDocument();
  });

  it("has no basic a11y violations", async () => {
    const { container } = render(
      <SchemaForm
        schema={{ "user.timezone_display": { type: "str" } }}
        values={{ "user.timezone_display": "UTC" }}
        saveLabel="Save"
        onSubmit={vi.fn()}
      />,
    );
    const results = await axe(container, { rules: { "color-contrast": { enabled: false } } });
    expect(results.violations).toHaveLength(0);
  });
});
