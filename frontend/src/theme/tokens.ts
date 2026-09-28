// Единый токен-слой карточки вызова: значения из макетов (pencil/design.pen) →
// theme-переменные Home Assistant с fallback. CSS custom properties наследуются
// сквозь shadow DOM — задаём `--mdr-*` на :host карточки, дочерние компоненты
// (call-stage, open-control) берут `var(--mdr-*)`. Никаких хардкод-hex в UI, кроме
// scrim и красного LIVE-бейджа. См. call-card-ux-production.md §12 + plan §Global Constraints.
import { css, type CSSResult } from "lit";

import type { CallPhase } from "../state-machine.js";

/** Токен-слой для `static styles`. Подключать первым: `styles = [egTokens, css\`…\`]`. */
export const egTokens: CSSResult = css`
  :host {
    --mdr-primary: var(--primary-color, #03a9f4);
    --mdr-success: var(--success-color, #4caf50);
    --mdr-error: var(--error-color, #ef5350);
    --mdr-warning: var(--warning-color, #ffb300);
    --mdr-text: var(--primary-text-color, #e8e8e8);
    --mdr-text-2: var(--secondary-text-color, #a6a6a6);
    --mdr-text-3: var(--disabled-text-color, #787878);
    --mdr-elevated: var(--secondary-background-color, #2a2a2a);
    --mdr-card: var(--ha-card-background, var(--card-background-color, #1c1c1c));
    --mdr-divider: var(--divider-color, #2e2e2e);
    --mdr-on-fill: var(--text-primary-color, #ffffff);
    --mdr-scrim: rgba(0, 0, 0, 0.72);
    --mdr-r-card: 16px;
    --mdr-r-md: 12px;
    --mdr-r-full: 999px;
    --mdr-mono: "Roboto Mono", ui-monospace, monospace;
    /* Тинты бейджей/баннеров = роль-цвет @ ~18% (эквивалент alpha 2E/1A из макета). */
    --mdr-primary-bg: color-mix(in srgb, var(--mdr-primary) 18%, transparent);
    --mdr-success-bg: color-mix(in srgb, var(--mdr-success) 18%, transparent);
    --mdr-error-bg: color-mix(in srgb, var(--mdr-error) 18%, transparent);
    --mdr-warning-bg: color-mix(in srgb, var(--mdr-warning) 18%, transparent);
  }
`;

/** Цвет статус-бейджа по фазе вызова (роль-переменная токен-слоя). */
const STATUS_COLOR: Record<CallPhase, string> = {
  idle: "var(--mdr-text-2)",
  ringing: "var(--mdr-warning)",
  connecting: "var(--mdr-primary)",
  active: "var(--mdr-success)",
  ended: "var(--mdr-text-2)",
  error: "var(--mdr-error)",
};

export function statusColor(phase: CallPhase): string {
  return STATUS_COLOR[phase] ?? "var(--mdr-text-2)";
}
