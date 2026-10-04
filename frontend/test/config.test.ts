import { describe, expect, it } from "vitest";
import { discoverCallConfig, discoverDoorbell, discoverHistoryConfig, type DiscoveryHass } from "../src/config.js";

const entity = (entity_id: string, device_id: string, translation_key?: string, platform = "my_dom_ru") =>
  ({ entity_id, device_id, translation_key, platform });
function fixture(): DiscoveryHass {
  const entities = [
    entity("sensor.renamed", "door1", "call_state"),
    entity("sensor.second", "door2", "call_state"),
    entity("sensor.foreign", "door1", "call_state", "other"),
    entity("camera.door1", "door1"), entity("lock.door1", "door1"),
    entity("camera.door2", "door2"), entity("lock.door2", "door2"),
    entity("camera.live", "live"),
    entity("event.place_renamed", "place", "account_history"),
    entity("event.door", "door1", "access_history"),
    entity("event.motion", "door1", "camera_history"),
  ];
  return {
    entities: Object.fromEntries(entities.map((item) => [item.entity_id, item])),
    states: Object.fromEntries(entities.map((item) => [item.entity_id, { state: "unavailable", attributes: {} }])),
    devices: { live: { identifiers: [["my_dom_ru", "entry_intercom_call"]] } },
  };
}

describe("card entity discovery", () => {
  it("matches renamed sensors, cameras and locks by integration and device", () => {
    expect(discoverCallConfig(fixture())).toEqual({
      doorbells: [
        { call_state: "sensor.renamed", doorbell_camera: "camera.door1", lock: "lock.door1" },
        { call_state: "sensor.second", doorbell_camera: "camera.door2", lock: "lock.door2" },
      ], camera: "camera.live", open_action: "slide",
    });
  });
  it("does not guess another door's lock or choose an ambiguous lock", () => {
    const hass = fixture();
    hass.entities!["lock.extra"] = entity("lock.extra", "door1");
    hass.states["lock.extra"] = { state: "locked", attributes: {} };
    expect(discoverDoorbell(hass, "sensor.renamed").lock).toBeUndefined();
    expect(discoverDoorbell(hass, "sensor.missing")).toEqual({ call_state: "sensor.missing" });
  });
  it("prefers aggregate history without including the same door twice or motion feeds", () => {
    expect(discoverHistoryConfig(fixture())).toEqual({ entities: ["event.place_renamed"] });
    const hass = fixture();
    delete hass.states["event.place_renamed"];
    expect(discoverHistoryConfig(hass)).toEqual({ entities: ["event.door"] });
  });
  it("returns empty editable configs when no registry or integration entities exist", () => {
    expect(discoverCallConfig()).toEqual({ doorbells: [], open_action: "slide" });
    expect(discoverHistoryConfig()).toEqual({ entities: [] });
  });
});
