/** Configuration and the public HA registry subset used by the card editors. */
export interface DoorbellConfig {
  call_state: string;
  doorbell_camera?: string;
  lock?: string;
  name?: string;
  address?: string;
}

export interface CallCardConfig {
  type?: string;
  camera?: string;
  doorbells?: DoorbellConfig[];
  call_state?: string;
  doorbell_camera?: string;
  lock?: string;
  name?: string;
  address?: string;
  open_action?: string;
  mic?: boolean;
  mic_autostart?: boolean;
  timer?: "auto" | "stopwatch" | "off";
  idle_text?: string;
  layout?: "compact" | "full";
}

export interface RegistryEntity {
  entity_id: string;
  platform?: string;
  translation_key?: string;
  device_id?: string | null;
}

export interface DiscoveryHass {
  states: Record<string, { state: string; attributes: Record<string, unknown> }>;
  entities?: Record<string, RegistryEntity>;
  devices?: Record<string, { identifiers?: [string, string][] }>;
  language?: string;
  locale?: { language?: string };
}

export function integrationEntities(hass?: DiscoveryHass): RegistryEntity[] {
  return Object.values(hass?.entities ?? {}).filter(
    (entity) => entity.platform === "my_dom_ru" && hass?.states[entity.entity_id],
  );
}

export function callStateEntities(hass?: DiscoveryHass): RegistryEntity[] {
  return integrationEntities(hass).filter(
    (entity) => entity.entity_id.startsWith("sensor.") && entity.translation_key === "call_state",
  );
}

export function discoverDoorbell(hass: DiscoveryHass | undefined, callState: string): DoorbellConfig {
  const sensor = hass?.entities?.[callState];
  const siblings = sensor?.device_id
    ? integrationEntities(hass).filter((entity) => entity.device_id === sensor.device_id)
    : [];
  const unique = (domain: string): string | undefined => {
    const matches = siblings.filter((entity) => entity.entity_id.startsWith(`${domain}.`));
    return matches.length === 1 ? matches[0].entity_id : undefined;
  };
  const camera = unique("camera");
  const lock = unique("lock");
  return {
    call_state: callState,
    ...(camera ? { doorbell_camera: camera } : {}),
    ...(lock ? { lock } : {}),
  };
}

export function discoverCallConfig(hass?: DiscoveryHass): CallCardConfig {
  const cameras = integrationEntities(hass).filter((entity) =>
    entity.entity_id.startsWith("camera.") && entity.device_id
    && hass?.devices?.[entity.device_id]?.identifiers?.some(
      ([domain, id]) => domain === "my_dom_ru" && id.endsWith("_intercom_call"),
    ),
  );
  return {
    doorbells: callStateEntities(hass).map((entity) => discoverDoorbell(hass, entity.entity_id)),
    ...(cameras.length === 1 ? { camera: cameras[0].entity_id } : {}),
    open_action: "slide",
  };
}

export function historyEntities(hass?: DiscoveryHass): RegistryEntity[] {
  return integrationEntities(hass).filter((entity) =>
    entity.entity_id.startsWith("event.")
    && ["account_history", "access_history"].includes(entity.translation_key ?? ""),
  );
}

export function discoverHistoryConfig(hass?: DiscoveryHass): { entities: string[] } {
  const entities = historyEntities(hass);
  const places = entities.filter((entity) => entity.translation_key === "account_history");
  return { entities: (places.length ? places : entities).map((entity) => entity.entity_id) };
}
