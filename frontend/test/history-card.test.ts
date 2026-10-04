import { describe, expect, it } from "vitest";

import { EgEventHistoryCard } from "../src/mdr-event-history-card.js";

describe("history card", () => {
  it("does not invent an entity when no HA registry is available", () => {
    expect(EgEventHistoryCard.getStubConfig()).toEqual({ entities: [] });
  });
});
