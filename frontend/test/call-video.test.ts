import { afterEach, describe, expect, it, vi } from "vitest";

import { EgCallVideo, pickCameraEntity } from "../src/components/call-video.js";

afterEach(() => vi.unstubAllGlobals());

it("loads the lazy HA camera module before choosing a provider", async () => {
  let ready = false;
  const createCardElement = vi.fn(() => { ready = true; });
  vi.stubGlobal("window", { loadCardHelpers: async () => ({ createCardElement }) });
  vi.stubGlobal("customElements", {
    get: (name: string) => name === "ha-camera-stream" && ready ? class {} : undefined,
    whenDefined: async () => {},
  });
  const video = new EgCallVideo() as unknown as {
    _resolveProvider: () => Promise<void>; _provider: string;
  };
  await video._resolveProvider();
  expect(createCardElement).toHaveBeenCalledWith({ type: "picture-glance", entities: [] });
  expect(video._provider).toBe("ha");
});

const cfg = { camera: "camera.intercom_call", doorbell_camera: "camera.podyezd_2" };

describe("pickCameraEntity", () => {
  it("active (video=call) → камера вызова (видео+звук)", () => {
    expect(pickCameraEntity("call", cfg)).toBe("camera.intercom_call");
  });

  it("ringing (video=doorbell) → камера домофона", () => {
    expect(pickCameraEntity("doorbell", cfg)).toBe("camera.podyezd_2");
  });

  it("doorbell без doorbell_camera → падает на camera", () => {
    expect(pickCameraEntity("doorbell", { camera: "camera.x" })).toBe("camera.x");
  });

  it("video=none → ничего", () => {
    expect(pickCameraEntity("none", cfg)).toBeUndefined();
  });
});
