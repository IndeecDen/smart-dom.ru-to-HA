# Умный Дом.ру для Home Assistant

<p align="center">
  <img src="custom_components/my_dom_ru/brand/logo.png" alt="Умный Дом.ру" width="180">
</p>

[![Release](https://img.shields.io/github/v/release/IndeecDen/smart-dom.ru-to-HA?label=Release)](https://github.com/IndeecDen/smart-dom.ru-to-HA/releases/latest)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41f5f4.svg)](https://hacs.xyz)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Неофициальная интеграция облака «Умный Дом.ру» (ЭР-Телеком, пакет
`com.ertelecom.smarthome`, профиль приложения 9.10.0) в Home Assistant.
Домофон, камеры, архив, входящий звонок с двусторонним звуком, история,
баланс, «Не беспокоить» и дополнительные действия для временных пропусков,
электронных ключей, настроек личных камер, документов и обращений.

> **Статус: 0.1.0, стабильный функционал не проверен на реальном аккаунте.**
> Код, контракты API и карточки покрыты тестами, но проверки входа в облако,
> живого звонка и физического открытия двери на конкретном адресе не было.
> Начинайте с [FEATURES.md](docs/FEATURES.md), где каждая функция отмечена по
> уровню подтверждения.

## Возможности

| Платформа HA | Что даёт |
|---|---|
| `lock` | Домофон, калитка, дверь/шлагбаум: открыть и состояние |
| `camera` | Личные и общедоступные камеры: снимок, поток HLS, RTSP для go2rtc |
| `event` | Вызов домофона, доступ по электронным ключам, события движения и обращений |
| `sensor` | Баланс, срок блокировки, RTSP-ссылки go2rtc, состояние звонка |
| `binary_sensor` | Признак блокировки лицевого счёта |
| `switch` | «Не беспокоить» для звонков домофона и от управляющей компании |
| `media_source` | Архив записей камер в медиатеке |

Дополнительно:

- **Входящий звонок.** FCM-уведомление оператора превращается в событие HA,
  отвечайте и завершайте звонок действиями `answer` / `hangup` или карточкой.
- **Двусторонний звук.** Собственный SIP-стек (диалог, SDP, RTP, STUN, Digest)
  работает без внешнего SIP-сервера; карточка микрофона управляет talk-сессией.
- **go2rtc.** Опционально: видео без него идёт через HLS, вместе с ним появляются
  RTSP-ссылки для `stream` и звук с камер.
- **30+ действий.** Пропуски, ключи, настройки камер, документы, обращения,
  финансы. Внутриквартирные идентификаторы получаются одним действием
  `my_dom_ru.get_inventory`.
- **Карточки Lovelace.** `custom:mdr-intercom-call-card` (звонок + микрофон) и
  `custom:mdr-event-history-card` (история событий).
- **Диагностика.** Кнопка загрузки отредактированной диагностики прямо из UI.

## Требования

- Home Assistant **2026.8.1** или новее.
- Договор «Дом.ру» с услугой «Умный Дом.ру» и телефон для кода входа.
- Python-зависимости ставятся Home Assistant автоматически из `manifest.json`
  (`firebase-messaging`, `audioop-lts` для Python 3.13+).
- Необязательно: доступный из HA [go2rtc](https://github.com/AlexxIT/go2rtc)
  для RTSP и звука.

## Установка

### HACS

1. Установите [HACS](https://hacs.xyz).
2. «HACS → Репозитории → ⋮ → Добавить репозиторий» →
   `https://github.com/IndeecDen/smart-dom.ru-to-HA`.
3. «HACS → Умный Дом.ру → Загрузить», затем перезапустите Home Assistant.

### Вручную

Скачайте `my_dom_ru-0.1.0-manual.zip` со страницы
[релизов](https://github.com/IndeecDen/smart-dom.ru-to-HA/releases) и распакуйте
в конфигурационный каталог HA так, чтобы получился путь
`custom_components/my_dom_ru/manifest.json`. Перезапустите Home Assistant.

### Первый запуск

1. «Настройки → Устройства и службы → Добавить интеграцию → Умный Дом.ру».
2. Введите номер телефона или договора, затем код из SMS или пароль — как
   предложит оператор.
3. При наличии go2rtc включите его в параметрах интеграции.
4. Проверьте снимок камеры, открытие двери и один звонок на **своём** домофоне.

Подробности, карточки и обновление: [docs/INSTALL.md](docs/INSTALL.md).

## Действия

| Действие | Назначение |
|---|---|
| `my_dom_ru.answer` / `my_dom_ru.hangup` | Ответить на вызов домофона / завершить разговор |
| `my_dom_ru.get_inventory` | `place_id`, внутренние `camera_id`, идентификаторы домофонов |
| `my_dom_ru.list_temp_passes` | Список временных пропусков |
| `my_dom_ru.temp_pass_options` | Какие двери разрешены для пропуска |
| `my_dom_ru.temp_pass_lifetimes` | Допустимые сроки действия пропуска |
| `my_dom_ru.create_temp_pass` / `delete_temp_pass` | Создать или удалить пропуск |
| `my_dom_ru.list_access_keys` | Список электронных ключей |
| `my_dom_ru.add_access_key` / `delete_access_key` | Добавить или удалить ключ |
| `my_dom_ru.reactivate_access_key` | Повторно активировать ключ |
| `my_dom_ru.rename_access_key` | Переименовать ключ |
| `my_dom_ru.toggle_key_notifications` | Переключить уведомления ключа |
| `my_dom_ru.camera_motion_parameters` | Диапазоны чувствительности движения |
| `my_dom_ru.camera_set_sensitivity` | Чувствительность обнаружения движения |
| `my_dom_ru.camera_set_recording` / `camera_set_event_recording` | Запись и запись по событиям |
| `my_dom_ru.camera_rename` | Переименовать камеру |
| `my_dom_ru.camera_mirror` | Отразить изображение |
| `my_dom_ru.camera_ptz` | `direction` + `movement: start\|stop` |
| `my_dom_ru.camera_audio_volumes` | Допустимые уровни громкости |
| `my_dom_ru.camera_set_microphone_volume` / `camera_set_speaker_volume` | Громкость камеры |
| `my_dom_ru.camera_features` | Возможности камеры |
| `my_dom_ru.get_finances` | Финансовая информация по адресу |
| `my_dom_ru.list_documents` / `acknowledge_document` | Документы по адресу |
| `my_dom_ru.list_requests` / `create_maintenance_request` | Обращения в УК |
| `my_dom_ru.get_screen_sections` | Разделы приложения для адреса |

Все, кроме `answer` и `hangup`, — действия администратора. Идентификаторы берутся
из `get_inventory`, значения перечислений — из соответствующих
`*_options` / `*_parameters` / `*_volumes`. После `camera_ptz` со значением `start`
всегда отправляйте `stop`, в том числе при ошибке автоматизации.

## Примеры Lovelace

```yaml
type: vertical-stack
cards:
  - type: custom:mdr-intercom-call-card
    entity: binary_sensor.moy_dom_lock
  - type: history-graph
    title: Баланс
    entities:
      - sensor.moy_dom_balance
```

## Кто открыл дверь

Оператор **не сообщает**, каким ключом открыли: в ответе есть только тип события
`accessKeyActivated`, время и готовый текст. Приложение само этот текст не
разбирает. Поэтому имена ключей задаются у вас в Home Assistant.

В параметрах интеграции заполните «Имена ключей», по одному в строке:

```
098b987y = Сын
098c112z = Жена
```

Код ключа возьмите из действия `my_dom_ru.list_access_keys` — поле
`accessKeyCode`. Сопоставление ищет код в тексте события в любом месте и в любом
регистре, поэтому формулировка оператора («Дверь открыта ключом X»,
«Доступ предоставлен: X») значения не имеет.

Событие приходит двумя путями: realtime-пушем FCM (за секунды) и опросом
истории раз в 5 минут (добор, если HA был выключен). Дубликаты отсекаются по
идентификатору события, поэтому уведомление придёт один раз.

Текст оператора в HA не попадает: наружу отдаётся только имя из вашего
сопоставления. Если код не сопоставлен, событие всё равно придёт, но без
атрибута `key_name`.

Уведомление в Telegram:

```yaml
triggers:
  - trigger: state
    entity_id: event.moy_dom_doorofon_access
    attribute: event_type
    to: key_activated
actions:
  - action: notify.telegram
    data:
      message: >-
        {% if trigger.event.data.key_name is defined %}
          {{ trigger.event.data.key_name }} открыл домофон
        {% else %}
          Кто-то открыл домофон ключом
        {% endif %}
```

Если сопоставление не заполнено, HA покажет «Дверь открыта ключом …» в истории
приложения, но `key_name` будет пустым. Проверить можно автоматизацией или
через `my_dom_ru.list_access_keys`.

## Автоматизации

Звонок с порога как триггер:

```yaml
triggers:
  - trigger: state
    entity_id: event.moy_dom_doorbell
    to: "on"
actions:
  - action: notify.mobile_app_phone
    data:
      message: "Звонок в домофон"
  - action: my_dom_ru.answer
```

Автоматическое открытие двери гостю по пропуску — по вашему усмотрению и
возможностям домофона: интеграция даёт сущность `lock`, а правило открытия
остаётся в HA.

## Ограничения

- Неофициальная интеграция: работает через облако оператора и его закрытый API.
  Изменения на стороне оператора могут сломать сборку без предупреждения.
- Платёжные операции, привязка камер по Wi-Fi, поиск по Bluetooth, гостевой QR
  вход и биометрия остаются в официальном приложении: они зависят от
  устройства, платёжного сервиса и непроверенных контрактов.
- Функции из последних строк [FEATURES.md](docs/FEATURES.md) не реализованы
  намеренно — не стоит угадывать платёжные и гостевые контракты по одному APK.
- Не запускайте один аккаунт одновременно в этой интеграции и в
  `elektronny_gorod`: получите параллельные FCM-подключения и двойной опрос облака.
- Домены у интеграций разные, они не конфликтуют по ресурсам.
- Реальная функциональность зависит от модели устройства, адреса и тарифа.

## Разработка

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.venv-ha/Scripts/python.exe -m pytest -p pytest_asyncio.plugin tests/unit tests/ha tests/portable -q
npm ci --prefix frontend
npm run typecheck --prefix frontend
npm test --prefix frontend
npm run build --prefix frontend
.venv/Scripts/python.exe tools/copy_licenses.py
.venv/Scripts/python.exe tools/package.py
```

`tools/package.py` собирает `dist/my_dom_ru.zip` (для HACS) и
`dist/my_dom_ru-<версия>-manual.zip` (ручная установка) по явному allowlist
файлов, затем пишет `dist/SHA256SUMS.txt`. Ни один архив не содержит APK,
декомпилированный код, токены или персональные данные.

Полный `pytest tests/` рассчитан на Linux (плагин
`pytest-homeassistant-custom-component` не работает на Windows из-за `fcntl`) и
прогоняется в CI: [.github/workflows/ci.yml](.github/workflows/ci.yml).
Подробнее: [docs/TESTING.md](docs/TESTING.md).

### Графика

Знак нарисован вручную и объединяет глиф дома оператора с синим Home
Assistant. Исходный PNG в репозитории не хранится; `make_brand.py` только
нормализует его — обрезает по содержимому, приводит к квадрату, добавляет
прозрачные поля и пишет шесть файлов, которые Home Assistant ожидает в
`custom_components/my_dom_ru/brand/`.

```powershell
.venv/Scripts/python.exe tools/make_brand.py "D:\downloads\smart.dom.ru.png"
.venv/Scripts/python.exe tools/make_social_preview.py
```

Прозрачность сохраняется намеренно: у знака белая обводка, и заливка на белый
фон нарисовала бы белый квадрат, который неверно выглядит на тёмной теме.
Проверки имён, сигнатуры PNG, квадратности и альфы — в
`tests/unit/test_brand_assets.py`.

Аватар и social preview репозитория API не позволяет задать (`PATCH` с полем
`avatar` молча игнорируется, `POST /social_preview` отдаёт 404) — только через
веб-интерфейс: репозиторий → About → Edit.

## Документация

- [docs/INSTALL.md](docs/INSTALL.md) — установка, HACS, карточки, обновление.
- [docs/FEATURES.md](docs/FEATURES.md) — что реализовано и что требует проверки.
- [docs/TESTING.md](docs/TESTING.md) — воспроизводимые проверки и их пределы.
- [docs/apk-api-9.10.0.json](docs/apk-api-9.10.0.json) — наблюдавшиеся
  декларации API из профиля приложения 9.10.0.
- [CHANGELOG.md](CHANGELOG.md) — история изменений.

## Сообщить о проблеме

Откройте [issue](https://github.com/IndeecDen/smart-dom.ru-to-HA/issues) и
приложите **отредактированную** диагностику из
«Настройки → Устройства и службы → Умный Дом.ру → ⋮ → Загрузить диагностику».

Не публикуйте пароли, коды из SMS, токены, ссылку временного пропуска, код
электронного ключа, полные логи, HAR-записи, экспорт `.storage`, APK и данные
гостей. Используйте только собственный аккаунт.

## Благодарности и лицензия

Основная реализация камер, SIP/FCM, архива, конфигурации и карточек основана на
MIT-проекте [gentslava/elektronny-gorod](https://github.com/gentslava/elektronny-gorod)
(commit `5d8aebaaa680fd0f9063643e400f895fdc674d62`, версия 4.1.0).
Подробности: [NOTICE.md](NOTICE.md). Лицензия проекта — [MIT](LICENSE).
Frontend использует Lit (BSD-3-Clause) и SVG-иконки Lucide (ISC); тексты
лицензий — в [THIRD_PARTY_LICENSES.txt](THIRD_PARTY_LICENSES.txt).

Название, пакет и логотипы «Умный Дом.ру» / ЭР-Телеком принадлежат их владельцам.
Проект не связан с оператором и не имеет его поддержки. Используйте его на свой
страх и риск: с облачными ключами отправка команд реальным устройствам.
Подробности: [DISCLAIMER.md](DISCLAIMER.md).
