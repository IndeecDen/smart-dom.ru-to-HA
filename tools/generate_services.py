"""Generate action descriptions and translations from the operation registry."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "custom_components/my_dom_ru"
spec = importlib.util.spec_from_file_location("app_api", BASE / "app_api.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

LABELS = {
    "get_inventory": "Адреса и идентификаторы устройств",
    "list_temp_passes": "Список временных пропусков",
    "temp_pass_options": "Доступные двери для пропуска",
    "temp_pass_lifetimes": "Допустимые сроки действия пропуска",
    "create_temp_pass": "Создать временный пропуск",
    "delete_temp_pass": "Удалить временный пропуск",
    "list_access_keys": "Список электронных ключей",
    "add_access_key": "Добавить электронный ключ",
    "delete_access_key": "Удалить электронный ключ",
    "reactivate_access_key": "Повторно активировать ключ",
    "rename_access_key": "Переименовать ключ",
    "toggle_key_notifications": "Переключить уведомления ключа",
    "camera_motion_parameters": "Параметры обнаружения движения",
    "camera_set_sensitivity": "Установить чувствительность движения",
    "camera_set_recording": "Включить или выключить запись",
    "camera_set_event_recording": "Запись по событиям",
    "camera_rename": "Переименовать камеру",
    "camera_mirror": "Отразить изображение камеры",
    "camera_ptz": "Повернуть или остановить камеру",
    "camera_audio_volumes": "Уровни и диапазоны громкости",
    "camera_set_microphone_volume": "Громкость микрофона камеры",
    "camera_set_speaker_volume": "Громкость динамика камеры",
    "camera_features": "Возможности камер",
    "get_finances": "Финансовая информация",
    "list_requests": "Список обращений",
    "create_maintenance_request": "Создать обращение в управляющую компанию",
    "list_documents": "Документы по адресу",
    "acknowledge_document": "Отметить документ прочитанным",
    "get_screen_sections": "Разделы приложения для адреса",
}
LABELS_EN = {
    "get_inventory": "Places and device IDs",
    "list_temp_passes": "List temporary passes",
    "temp_pass_options": "Eligible doors for a temporary pass",
    "temp_pass_lifetimes": "Available pass lifetimes",
    "create_temp_pass": "Create a temporary pass",
    "delete_temp_pass": "Delete a temporary pass",
    "list_access_keys": "List access keys",
    "add_access_key": "Add an access key",
    "delete_access_key": "Delete an access key",
    "reactivate_access_key": "Reactivate an access key",
    "rename_access_key": "Rename an access key",
    "toggle_key_notifications": "Toggle key notifications",
    "camera_motion_parameters": "Camera motion settings",
    "camera_set_sensitivity": "Set motion sensitivity",
    "camera_set_recording": "Set camera recording",
    "camera_set_event_recording": "Set event recording",
    "camera_rename": "Rename a camera",
    "camera_mirror": "Mirror a camera image",
    "camera_ptz": "Start or stop camera movement",
    "camera_audio_volumes": "Camera audio volume settings",
    "camera_set_microphone_volume": "Set camera microphone volume",
    "camera_set_speaker_volume": "Set camera speaker volume",
    "camera_features": "Camera features",
    "get_finances": "Financial information",
    "list_requests": "List maintenance requests",
    "create_maintenance_request": "Create a maintenance request",
    "list_documents": "List documents",
    "acknowledge_document": "Acknowledge a document",
    "get_screen_sections": "App sections for a place",
}
FIELDS = {
    "config_entry_id": ("Учётная запись", "Выберите загруженную запись Умный Дом.ру."),
    "place_id": ("Адрес (ID)", "Получите через my_dom_ru.get_inventory."),
    "camera_id": ("Камера (внутренний ID)", "Используйте personal_cameras.camera_id из get_inventory, не externalCameraId."),
    "pass_id": ("Пропуск (ID)", "Получите через list_temp_passes."),
    "key_id": ("Услуга ключа (ID)", "Поле id из list_access_keys, не вложенный accessKey.id."),
    "key_code": ("Код ключа", "Код вашего физического ключа. Не публикуйте трассировку автоматизации с этим полем."),
    "ttl": ("Срок действия", "Передайте одно из значений temp_pass_lifetimes без преобразования единиц."),
    "access_control_ids": ("Домофоны (ID)", "Список из temp_pass_options: например [101, 102]."),
    "name": ("Название", "Новое название в облаке оператора."),
    "mode": ("Запись", "on — запись включена, off — выключена."),
    "enabled": ("Включено", "Включить запись по событиям."),
    "sensitivity": ("Чувствительность", "Допустимый диапазон проверяется по camera_motion_parameters."),
    "axis": ("Ось отражения", "vertical или horizontal. Это команда изменения, а не сохранённое состояние."),
    "direction": ("Направление", "Направление поворота камеры."),
    "movement": ("Действие", "После start обязательно отправьте stop; для автоматизаций задайте короткую задержку."),
    "volume": ("Громкость", "Одно из значений диапазона camera_audio_volumes."),
    "page": ("Страница", "Нумерация с нуля."),
    "document_id": ("Документ (ID)", "Получите через list_documents для этого же адреса."),
    "phone": ("Телефон", "Контактный номер для обращения."),
    "full_name": ("Имя", "Имя отправителя для обращения."),
    "message": ("Текст обращения", "Сообщение для управляющей компании."),
}
FIELDS_EN = {
    "config_entry_id": "Account", "place_id": "Place ID", "camera_id": "Internal camera ID",
    "pass_id": "Pass ID", "key_id": "Key service ID", "key_code": "Key code",
    "ttl": "Lifetime", "access_control_ids": "Access control IDs", "name": "Name",
    "mode": "Recording mode", "enabled": "Enabled", "sensitivity": "Sensitivity",
    "axis": "Mirror axis", "direction": "Direction", "movement": "Movement",
    "volume": "Volume", "page": "Page", "document_id": "Document ID",
    "phone": "Phone", "full_name": "Full name", "message": "Message",
}
CHOICES = {"mode": ["on", "off"], "axis": ["vertical", "horizontal"], "direction": ["up", "down", "left", "right"], "movement": ["start", "stop"]}


def selector(field: str) -> dict:
    if field == "config_entry_id":
        return {"config_entry": {"integration": "my_dom_ru"}}
    if field == "enabled":
        return {"boolean": {}}
    if field in CHOICES:
        return {"select": {"options": CHOICES[field]}}
    if field == "access_control_ids":
        return {"object": {}}
    if field in ("ttl", "sensitivity", "volume", "page"):
        return {"number": {"min": 0 if field != "ttl" else 1, "max": 2147483647, "mode": "box", "step": 1}}
    return {"text": {}}


if __name__ == "__main__":
    path = BASE / "services.yaml"
    services = yaml.safe_load(path.read_text(encoding="utf-8"))
    for operation, label in LABELS.items():
        fields = ["config_entry_id"]
        if operation != "get_inventory":
            op = module.OPERATIONS[operation]
            fields += ["place_id"] + (["camera_id"] if op.camera else []) + list(op.fields)
        description = "Действие администратора. Возможность должна поддерживаться устройством и тарифом оператора."
        if operation == "create_temp_pass":
            description += " Возвращает пропуск и текст ссылки в result; никаких сообщений гостю не отправляет."
        if operation == "toggle_key_notifications":
            description += " Переключает текущее значение; повторный вызов переключит его обратно."
        if operation == "camera_ptz":
            description += " После start отправьте stop даже при ошибке автоматизации."
        if operation == "create_maintenance_request":
            description += " Однократно отправляет текст и контактный номер оператору."
        services[operation] = {
            "name": label, "description": description,
            "fields": {field: {
                "name": FIELDS[field][0], "description": FIELDS[field][1],
                "required": field != "page", "selector": selector(field),
                **({"default": 0} if field == "page" else {}),
            } for field in fields},
        }
    path.write_text(yaml.safe_dump(services, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for path in [BASE / 'strings.json', *sorted((BASE / 'translations').glob('*.json'))]:
        translations = json.loads(path.read_text(encoding='utf-8'))
        translated = translations.setdefault('services', {})
        english = path.name != 'ru.json'
        for key in LABELS:
            translated[key] = {"name": LABELS_EN[key] if english else LABELS[key],
                               "description": ("Administrator action. Requires device and subscription support." if english else services[key]["description"])}
            translated[key]['fields'] = {field: {
                'name': FIELDS_EN[field] if english else info['name'],
                'description': ("Use the matching ID or value returned by this integration." if english else info['description']),
            } for field, info in services[key]['fields'].items()}
        path.write_text(json.dumps(translations, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Generated descriptions for {len(LABELS)} app actions')
