// Видео-область экрана вызова: chromeless-плеер (mdr-call-video) + оверлеи
// (LIVE-бейдж, таймстамп, чип «Звук вкл.», CTA «включить звук») + плейсхолдеры
// (камера недоступна / связь прервана) + tap-to-unmute. Облик — по макетам
// pencil/design.pen (компонент CallVideo + узлы camera_unavailable/connection_lost).
// Единственные хардкод-цвета — scrim и красный LIVE (разрешённые исключения).
import { LitElement, css, html, nothing, type TemplateResult } from "lit";
import { customElement, property } from "lit/decorators.js";

import { egTokens } from "../theme/tokens.js";
import { type Lang, t } from "../i18n.js";
import "./call-video.js";
import "./mdr-icon.js";

interface HassLike {
  states: Record<string, { state: string; attributes: Record<string, unknown> }>;
  connection?: unknown;
}

export type StageState = "live" | "camera_off" | "connection_lost" | "ended";
export type StageContent = "video" | "placeholder-camera" | "placeholder-connection" | "video-dimmed";

/** Что рендерить в видео-области по состоянию стейджа (чистая — юнит-тест). */
export function pickStageContent(state: StageState): StageContent {
  switch (state) {
    case "camera_off":
      return "placeholder-camera";
    case "connection_lost":
      return "placeholder-connection";
    case "ended":
      return "video-dimmed";
    default:
      return "video";
  }
}

@customElement("mdr-call-stage")
export class EgCallStage extends LitElement {
  @property({ attribute: false }) public hass?: HassLike;
  @property() public entity?: string;
  @property({ type: Boolean }) public muted = false;
  /** Показать красный бейдж LIVE. */
  @property({ type: Boolean }) public live = false;
  /** Показать чип «Звук выкл.» (звук выключен пользователем) — подсказка, почему тихо. */
  @property({ type: Boolean }) public soundOff = false;
  /** Таймстамп потока (bottom-left), пусто = скрыт. */
  @property() public stageState: StageState = "live";
  /** Автоплей со звуком заблокирован — CTA + тап по всему видео снимают mute. */
  @property({ type: Boolean }) public audioBlocked = false;
  /** Язык (ru/en) — прокидывается картой. */
  @property() public uiLang: Lang = "ru";

  private _unmute = (): void => {
    this.dispatchEvent(new CustomEvent("unmute", { bubbles: true, composed: true }));
  };

  protected override render(): TemplateResult {
    const s = t(this.uiLang);
    const content = pickStageContent(this.stageState);
    if (content === "placeholder-camera") {
      return this._placeholder("video-off", "muted", s.stage.cameraOff.title, s.stage.cameraOff.sub);
    }
    if (content === "placeholder-connection") {
      return this._placeholder("wifi-off", "err", s.stage.connectionLost.title, s.stage.connectionLost.sub);
    }
    return html`
      <mdr-call-video .hass=${this.hass} .uiLang=${this.uiLang} .entity=${this.entity} .muted=${this.muted}></mdr-call-video>
      ${content === "video-dimmed" ? html`<div class="dim" aria-hidden="true"></div>` : nothing}
      <div class="top">
        ${this.live
          ? html`<span class="live"><span class="live-dot" aria-hidden="true"></span>LIVE</span>`
          : nothing}
        ${this.soundOff
          ? html`<span class="chip"><mdr-icon name="volume-x"></mdr-icon>${s.stage.soundOffChip}</span>`
          : nothing}
      </div>
      ${this.audioBlocked
        ? html`
            <button class="tap" @click=${this._unmute} aria-label=${s.stage.unmuteAria}></button>
            <span class="cta" aria-hidden="true">
              <mdr-icon name="volume-x"></mdr-icon>${s.stage.unmuteCta}
            </span>
          `
        : nothing}
    `;
  }

  private _placeholder(icon: string, tone: string, title: string, sub: string): TemplateResult {
    return html`
      <div class="fallback ${tone}" role="img" aria-label=${title}>
        <mdr-icon name=${icon}></mdr-icon>
        <span class="fb-title">${title}</span>
        <span class="fb-sub">${sub}</span>
      </div>
    `;
  }

  static override styles = [
    egTokens,
    css`
      :host {
        position: absolute;
        inset: 0;
        display: block;
      }
      mdr-call-video {
        position: absolute;
        inset: 0;
      }
      .dim {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
      }
      /* верхний ряд оверлеев: LIVE (слева) + чип звука (справа) */
      .top {
        position: absolute;
        top: calc(12px * var(--mdr-scale, 1));
        left: calc(12px * var(--mdr-scale, 1));
        right: calc(12px * var(--mdr-scale, 1));
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        pointer-events: none;
      }
      .live {
        display: inline-flex;
        align-items: center;
        gap: calc(6px * var(--mdr-scale, 1));
        padding: calc(3px * var(--mdr-scale, 1)) calc(9px * var(--mdr-scale, 1));
        border-radius: var(--mdr-r-full);
        background: rgba(211, 47, 47, 0.88);
        color: #fff;
        font-size: calc(10px * var(--mdr-scale, 1));
        font-weight: 600;
        letter-spacing: 0.04em;
      }
      .live-dot {
        width: calc(6px * var(--mdr-scale, 1));
        height: calc(6px * var(--mdr-scale, 1));
        border-radius: 50%;
        background: #fff;
      }
      .chip {
        display: inline-flex;
        align-items: center;
        gap: calc(6px * var(--mdr-scale, 1));
        padding: calc(5px * var(--mdr-scale, 1)) calc(10px * var(--mdr-scale, 1));
        border-radius: var(--mdr-r-full);
        background: rgba(0, 0, 0, 0.63);
        color: #fff;
        font-size: calc(11px * var(--mdr-scale, 1));
      }
      .chip mdr-icon {
        --mdr-icon-size: calc(14px * var(--mdr-scale, 1));
      }
      /* CTA «включить звук» + прозрачный tap-слой поверх всего видео */
      .tap {
        position: absolute;
        inset: 0;
        border: none;
        background: transparent;
        cursor: pointer;
        z-index: 2;
      }
      /* CTA — в НИЖНЕЙ части видео (не перекрывает лицо звонящего), UX §8/§13 */
      .cta {
        position: absolute;
        left: 50%;
        bottom: calc(16px * var(--mdr-scale, 1));
        transform: translateX(-50%);
        display: inline-flex;
        align-items: center;
        gap: calc(8px * var(--mdr-scale, 1));
        padding: calc(10px * var(--mdr-scale, 1)) calc(18px * var(--mdr-scale, 1));
        border-radius: var(--mdr-r-full);
        background: var(--mdr-scrim);
        color: #fff;
        font-size: calc(13px * var(--mdr-scale, 1));
        font-weight: 500;
        white-space: nowrap;
        z-index: 3;
        pointer-events: none;
      }
      .cta mdr-icon {
        --mdr-icon-size: calc(18px * var(--mdr-scale, 1));
      }
      /* плейсхолдеры (камера недоступна / связь прервана) */
      .fallback {
        position: absolute;
        inset: 0;
        background: var(--mdr-card);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: calc(6px * var(--mdr-scale, 1));
        text-align: center;
        padding: calc(12px * var(--mdr-scale, 1));
        box-sizing: border-box;
      }
      .fallback mdr-icon {
        --mdr-icon-size: calc(36px * var(--mdr-scale, 1));
        color: var(--mdr-text-3);
      }
      .fallback.err mdr-icon {
        color: var(--mdr-error);
      }
      .fb-title {
        font-size: calc(15px * var(--mdr-scale, 1));
        color: var(--mdr-text);
      }
      .fb-sub {
        font-size: calc(12px * var(--mdr-scale, 1));
        color: var(--mdr-text-2);
      }
    `,
  ];
}
