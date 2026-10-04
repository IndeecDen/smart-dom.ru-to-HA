import { LitElement, css, html, type TemplateResult } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import {
  callStateEntities, discoverCallConfig, discoverDoorbell, discoverHistoryConfig, historyEntities,
  type CallCardConfig, type DiscoveryHass, type DoorbellConfig,
} from "./config.js";
import { langOf } from "./i18n.js";

type FormData = Record<string, unknown>;
type FormChange = CustomEvent<{ value: FormData }>;
type Field = { name: string; selector: Record<string, unknown> };

export async function createCardEditor(tag: string): Promise<HTMLElement> {
  if (!customElements.get("ha-form")) {
    // HA loads its form lazily with native card editors. Use the public card
    // helper rather than importing a hashed frontend chunk by URL.
    const helpers = await (window as unknown as {
      loadCardHelpers: () => Promise<{ createCardElement: (config: object) => HTMLElement }>;
    }).loadCardHelpers();
    helpers.createCardElement({ type: "entities", entities: [] });
    const native = await customElements.whenDefined("hui-entities-card");
    await (native as typeof HTMLElement & {
      getConfigElement: () => Promise<HTMLElement>;
    }).getConfigElement();
    await customElements.whenDefined("ha-form");
  }
  return document.createElement(tag);
}

const LABELS: Record<string, [string, string]> = {
  call_state: ["Состояние вызова", "Call state"],
  doorbell_camera: ["Камера домофона", "Doorbell camera"],
  camera: ["Камера разговора (необязательно)", "Call camera (optional)"],
  lock: ["Замок домофона", "Door lock"],
  name: ["Название домофона", "Doorbell name"],
  address: ["Адрес", "Address"],
  entities: ["Источники истории", "History sources"],
  title: ["Заголовок", "Title"],
  open_action: ["Способ открытия", "Open action"],
  layout: ["Размер карточки", "Card layout"],
  mic: ["Микрофон", "Microphone"],
  mic_autostart: ["Включать микрофон при ответе", "Start microphone on answer"],
  timer: ["Таймер", "Timer"],
  idle_text: ["Текст вне вызова", "Idle text"],
};

class CardEditor extends LitElement {
  @property({ attribute: false }) public hass?: DiscoveryHass;
  protected text(ru: string, en: string): string { return langOf(this.hass) === "en" ? en : ru; }
  private readonly _label = (field: { name: string }): string => {
    const labels = LABELS[field.name];
    return labels ? this.text(...labels) : field.name;
  };
  protected entity(name: string, domain: string, ids?: string[], multiple = false): Field {
    return { name, selector: { entity: {
      filter: { domain, integration: "my_dom_ru" },
      ...(ids?.length ? { include_entities: ids } : {}),
      ...(multiple ? { multiple: true } : {}),
    } } };
  }
  protected form(data: object, schema: Field[], change: (event: FormChange) => void): TemplateResult {
    return html`<ha-form .hass=${this.hass} .data=${data} .schema=${schema}
      .computeLabel=${this._label} @value-changed=${change}></ha-form>`;
  }
  protected emit(config: object): void {
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config }, bubbles: true, composed: true }));
  }
  static override styles = css`
    :host { display: block; }
    p { color: var(--secondary-text-color); line-height: 1.5; }
    fieldset { border: 1px solid var(--divider-color); border-radius: 12px; margin: 16px 0; padding: 16px; min-width: 0; }
    legend { padding: 0 8px; }
    button { font: inherit; color: var(--primary-color); background: transparent; border: 1px solid var(--divider-color); border-radius: 8px; padding: 10px 16px; cursor: pointer; margin: 8px 8px 8px 0; }
  `;
}

@customElement("mdr-intercom-call-card-editor")
export class CallCardEditor extends CardEditor {
  @state() private _config: CallCardConfig = {};

  public setConfig(config: CallCardConfig): void {
    const { call_state, doorbell_camera, lock, ...rest } = config;
    this._config = { ...rest, doorbells: config.doorbells ?? (call_state
      ? [{ call_state, doorbell_camera, lock, name: config.name, address: config.address }] : []) };
  }
  private _save(config: CallCardConfig): void { this._config = config; this.emit(config); }
  private _doorbellChange(index: number, event: FormChange): void {
    event.stopPropagation();
    const doorbells = [...(this._config.doorbells ?? [])];
    const previous = doorbells[index];
    let next = { ...previous, ...event.detail.value } as DoorbellConfig;
    next.call_state ||= "";
    if (next.call_state !== previous.call_state) {
      // Never carry a previous door's opening command to a newly selected sensor.
      const { lock: _lock, doorbell_camera: _camera, ...rest } = next;
      next = { ...rest, ...discoverDoorbell(this.hass, next.call_state) };
    }
    doorbells[index] = next;
    this._save({ ...this._config, doorbells });
  }
  protected override render(): TemplateResult {
    const select = (name: string, options: [string, string, string][]): Field => ({ name, selector: {
      select: { mode: "dropdown", options: options.map(([value, ru, en]) => ({ value, label: this.text(ru, en) })) },
    } });
    return html`
      <p>${this.text("Выберите сущности своего домофона. Камера и замок подбираются по тому же устройству.",
        "Select your doorbell entities. Camera and lock are matched by device.")}</p>
      <button @click=${() => this._save({ ...this._config, ...discoverCallConfig(this.hass) })}>
        ${this.text("Подобрать автоматически", "Detect entities")}</button>
      ${(this._config.doorbells ?? []).map((doorbell, index) => html`<fieldset>
        <legend>${this.text("Домофон", "Doorbell")} ${index + 1}</legend>
        ${this.form(doorbell, [
          this.entity("call_state", "sensor", callStateEntities(this.hass).map((entity) => entity.entity_id)),
          this.entity("doorbell_camera", "camera"), this.entity("lock", "lock"),
          { name: "name", selector: { text: {} } }, { name: "address", selector: { text: {} } },
        ], (event) => this._doorbellChange(index, event))}
        <button @click=${() => this._save({ ...this._config, doorbells: this._config.doorbells?.filter((_, i) => i !== index) })}>
          ${this.text("Удалить домофон", "Remove doorbell")}</button>
      </fieldset>`)}
      <button @click=${() => this._save({ ...this._config, doorbells: [...(this._config.doorbells ?? []), { call_state: "" }] })}>
        ${this.text("Добавить домофон", "Add doorbell")}</button>
      ${this.form({ open_action: "auto", layout: "full", timer: "auto", mic: true, mic_autostart: true, ...this._config }, [
        this.entity("camera", "camera"),
        select("open_action", [["auto", "Автоматически", "Automatic"], ["slide", "Слайдер", "Slide"], ["hold", "Удержание", "Hold"], ["tap", "Нажатие", "Tap"]]),
        select("layout", [["full", "Полная", "Full"], ["compact", "Компактная", "Compact"]]),
        select("timer", [["auto", "Автоматически", "Automatic"], ["stopwatch", "Секундомер", "Stopwatch"], ["off", "Выключен", "Off"]]),
        { name: "mic", selector: { boolean: {} } }, { name: "mic_autostart", selector: { boolean: {} } },
        { name: "idle_text", selector: { text: {} } },
      ], (event) => { event.stopPropagation(); this._save({ ...this._config, ...event.detail.value }); })}
    `;
  }
}

@customElement("mdr-event-history-card-editor")
export class HistoryCardEditor extends CardEditor {
  @state() private _config: FormData = {};
  public setConfig(config: FormData): void {
    const { entity, entities, ...rest } = config;
    this._config = { ...rest, entities: [...new Set([
      ...(typeof entity === "string" && entity ? [entity] : []),
      ...(Array.isArray(entities) ? entities : []),
    ])] };
  }
  private _save(config: FormData): void { this._config = config; this.emit(config); }
  protected override render(): TemplateResult {
    return html`
      <p>${this.text("Выберите историю адреса или отдельного домофона. История адреса уже включает его домофоны.",
        "Select a place or doorbell history. Place history already includes its doorbells.")}</p>
      <button @click=${() => this._save({ ...this._config, ...discoverHistoryConfig(this.hass) })}>
        ${this.text("Подобрать автоматически", "Detect entities")}</button>
      ${this.form(this._config, [
        this.entity("entities", "event", historyEntities(this.hass).map((entity) => entity.entity_id), true),
        { name: "title", selector: { text: {} } },
      ], (event) => { event.stopPropagation(); this._save({ ...this._config, ...event.detail.value }); })}
    `;
  }
}
