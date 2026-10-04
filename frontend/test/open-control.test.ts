import { describe, expect, it, vi } from "vitest";

import {
  clamp01,
  EgOpenControl,
  holdProgress,
  SLIDE_COMPLETE,
  slideProgress,
} from "../src/components/open-control.js";

// The Node Lit shim has no pointer dispatch, so drive the actual handlers
// with the same event objects while observing the externally emitted command.
function control() {
  const el = new EgOpenControl();
  const internals = el as unknown as {
    _arming: boolean; _pointerId: number | null; _progress: number;
    _onSlideUp: (e: PointerEvent) => void;
    _onPointerCancel: (e: PointerEvent) => void;
    _onTap: () => void;
    updated: (changed: Map<string, unknown>) => void;
  };
  const dispatch = vi.fn(() => true);
  el.dispatchEvent = dispatch;
  internals._arming = true;
  internals._pointerId = 1;
  internals._progress = 1;
  return { el, internals, dispatch };
}

describe("open gestures", () => {
  it("cancel at the end of the track never opens the door", () => {
    const { internals, dispatch } = control();
    internals._onPointerCancel({ pointerId: 1 } as PointerEvent);
    internals._onSlideUp({ pointerId: 1 } as PointerEvent);
    expect(dispatch).not.toHaveBeenCalled();
    expect(internals._progress).toBe(0);
  });

  it("ignores another pointer and commits the original gesture once", () => {
    const { internals, dispatch } = control();
    internals._onSlideUp({ pointerId: 2 } as PointerEvent);
    expect(dispatch).not.toHaveBeenCalled();
    internals._onSlideUp({ pointerId: 1 } as PointerEvent);
    internals._onTap();
    expect(dispatch).toHaveBeenCalledTimes(1);
  });

  it("disabling during a drag prevents its completion", () => {
    const { el, internals, dispatch } = control();
    el.disabled = true;
    internals._onSlideUp({ pointerId: 1 } as PointerEvent);
    expect(dispatch).not.toHaveBeenCalled();
  });

  it("blocks repeated taps until the card resets the result", () => {
    const { el, internals, dispatch } = control();
    internals._onTap();
    internals._onTap();
    expect(dispatch).toHaveBeenCalledTimes(1);
    el.status = "error";
    internals.updated(new Map([["status", "opening"]]));
    internals._onTap();
    expect(dispatch).toHaveBeenCalledTimes(2);
  });
});

describe("clamp01", () => {
  it("зажимает в [0..1]", () => {
    expect(clamp01(-0.5)).toBe(0);
    expect(clamp01(0.5)).toBe(0.5);
    expect(clamp01(1.5)).toBe(1);
  });
});

describe("slideProgress", () => {
  it("в начале дорожки ≈ 0", () => {
    // указатель у левого края (с поправкой на полузнобу) → 0
    expect(slideProgress(0 + 28, 0, 300, 56)).toBeCloseTo(0, 1);
  });
  it("в конце дорожки = 1", () => {
    expect(slideProgress(300, 0, 300, 56)).toBe(1);
  });
  it("по центру ~0.5", () => {
    expect(slideProgress(150, 0, 300, 56)).toBeCloseTo(0.5, 1);
  });
  it("учитывает смещение дорожки (trackLeft)", () => {
    expect(slideProgress(1000, 1000, 300, 56)).toBeCloseTo(0, 1);
    expect(slideProgress(1300, 1000, 300, 56)).toBe(1);
  });
  it("knob 68 (макет): край справа завершает, центр kнопки у левого края ≈ 0", () => {
    expect(slideProgress(300, 0, 300, 68)).toBeGreaterThanOrEqual(SLIDE_COMPLETE);
    expect(slideProgress(34, 0, 300, 68)).toBeCloseTo(0, 1);
  });
});

describe("holdProgress", () => {
  it("0 в начале, 1 по завершении, насыщается", () => {
    expect(holdProgress(0, 800)).toBe(0);
    expect(holdProgress(400, 800)).toBeCloseTo(0.5, 5);
    expect(holdProgress(800, 800)).toBe(1);
    expect(holdProgress(2000, 800)).toBe(1);
  });
});

describe("константы порогов", () => {
  it("slide завершается не на самом конце (анти-перелёт)", () => {
    expect(SLIDE_COMPLETE).toBeGreaterThan(0.8);
    expect(SLIDE_COMPLETE).toBeLessThan(1);
  });
});
