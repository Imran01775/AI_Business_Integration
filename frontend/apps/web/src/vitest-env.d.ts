/// <reference types="vitest/globals" />
/// <reference types="@testing-library/jest-dom" />

import type { AxeResults } from "axe-core";

declare module "vitest" {
  interface Assertion<T = unknown> {
    toHaveNoViolations(): T extends AxeResults ? void : never;
  }
}
