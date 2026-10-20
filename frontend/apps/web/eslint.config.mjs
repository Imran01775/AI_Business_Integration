import base from "@sales-agent/eslint-config";
import boundaries from "eslint-plugin-boundaries";

/** @type {import("eslint").Linter.Config[]} */
export default [
  ...base,
  {
    files: ["src/**/*.{ts,tsx}"],
    plugins: { boundaries },
    settings: {
      "boundaries/elements": [
        { type: "feature", pattern: "src/features/*" },
        { type: "shared", pattern: "src/shared/*" },
        { type: "app", pattern: "src/app/*" },
      ],
    },
    rules: {
      "boundaries/element-types": [
        "error",
        {
          default: "disallow",
          rules: [
            { from: "app", allow: ["feature", "shared", "app"] },
            { from: "feature", allow: ["shared", "feature"] },
            { from: "shared", allow: ["shared"] },
          ],
        },
      ],
    },
  },
];
