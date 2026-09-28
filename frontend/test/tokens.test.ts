import { describe, expect, it } from "vitest";

import { egTokens, statusColor } from "../src/theme/tokens.js";

describe("tokens", () => {
  it("статус-цвет по фазе — роль-переменная", () => {
    expect(statusColor("ringing")).toBe("var(--mdr-warning)");
    expect(statusColor("connecting")).toBe("var(--mdr-primary)");
    expect(statusColor("active")).toBe("var(--mdr-success)");
    expect(statusColor("error")).toBe("var(--mdr-error)");
    expect(statusColor("ended")).toBe("var(--mdr-text-2)");
    expect(statusColor("idle")).toBe("var(--mdr-text-2)");
  });

  it("egTokens содержит маппинг primary на HA-переменную и радиусы", () => {
    expect(egTokens.cssText).toContain("--mdr-primary: var(--primary-color");
    expect(egTokens.cssText).toContain("--mdr-r-full: 999px");
  });
});
