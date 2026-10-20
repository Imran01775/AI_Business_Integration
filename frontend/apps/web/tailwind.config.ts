import type { Config } from "tailwindcss";

import { salesAgentPreset } from "@sales-agent/design-tokens";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  presets: [salesAgentPreset],
};

export default config;
