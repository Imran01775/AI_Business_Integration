import "@testing-library/jest-dom/vitest";
import "vitest-axe/extend-expect";

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

globalThis.ResizeObserver = ResizeObserverMock;
