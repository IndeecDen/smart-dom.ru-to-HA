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

> **Статус: 0.1.1, интеграция использует закрытое облако оператора.**
> Получение FCM-уведомлений и распознавание прохода по ключу проверялись на
> реальном аккаунте. Остальные функции зависят от адреса, тарифа и устройства;
> сквозная проверка всех команд и потоков на разных установках не проводилась.
> Начинайте с [FEATURES.md](docs/FEATURES.md), где каждая функция отмечена по
> уровню подтверждения.

## Возможности

| Платформа HA | Что даёт |
|---|---|
| `lock` | Домофон, калитка, дверь/шлагбаум: открыть и состояние |
| `camera` | Камеры домофона, личные, общедоступные и соседних подъездов: снимок, HLS, опциональный RTSP через go2rtc |
| `event` | Звонок в домофон, история вызовов и проходов по ключу, движение домофонных и общедоступных камер |
| `sensor` | Баланс, срок блокировки, RTSP-ссылки go2rtc, состояние звонка |
| `binary_sensor` | Признак блокировки лицевого счёта |
| `switch` | «Не беспокоить» для звонков домофона и от управляющей компании |
| `media_source` | Архив записей камер в медиатеке |

Дополнительно:

- **Входящий звонок.** FCM-уведомление оператора превращается в событие HA,
  отвечайте и завершайте звонок действиями `answer` / `hangup` или карточкой.
- **Двусторонний звук.** Собственный SIP-стек (диалог, SDP, RTP, STUN, Digest)
  работает без внешнего SIP-сервера; карточка микрофона управляет talk-сессией.
- **Камеры соседних подъездов.** Интеграция читает разделы `screen-sections`
  для каждого адреса и создаёт сущности для камер с доступным видео и активной
  услугой. Их наличие определяется ответом оператора и подпиской; настройки
  скрытия камер в приложении учитываются.
- **go2rtc.** Опционально: видео без него идёт через HLS, вместе с ним доступны
  звук и публикуемые RTSP-ссылки. Датчик «Опубликованные RTSP-потоки» показывает
  только активные и подтверждённые регистрации, поэтому его значение может
  быть нулём даже при наличии сущности камеры.
- **30+ действий.** Пропуски, ключи, настройки камер, документы, обращения,
  финансы. Внутриквартирные идентификаторы получаются одним действием
  `my_dom_ru.get_inventory`.
- **Карточки Lovelace.** `custom:mdr-intercom-call-card` (звонок),
  `custom:mdr-intercom-mic-card` (микрофон) и
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

Скачайте `my_dom_ru-0.1.1-manual.zip` со страницы
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

Настраивать ничего не нужно: имена берутся из облака, те же, что вы задали в
приложении. Переименовали ключ в приложении — здесь он тоже переименуется.

Как это работает. Оператор не сообщает, каким ключом открыли: в ответе есть тип
события, время и готовый текст. В проверенном тексте имя уже есть —
`Улица 1 (п. 3) открыта ключом Иван.` — а тип события приходит
`infoNotification`, и `accessKeyActivated` в `events/search` не появляется
никогда. Приложение этот текст само не разбирает.

Интеграция сопоставляет текст с ключами из `list_access_keys` — и по имени, и
по коду, потому что оператор пишет любую из форм. Сравнение идёт по границам
слов, поэтому формулировка значения не имеет, а ключ с именем «Дом» не
находится внутри слова «Домофон».

Событие приходит двумя путями: realtime-пушем FCM (за секунды) и опросом
истории раз в 5 минут (добор, если HA был выключен). Дубликаты отсекаются по
идентификатору события, поэтому уведомление придёт один раз.

Текст оператора в HA не попадает: наружу отдаётся только имя. Если имя
оператора в тексте не встретилось, событие всё равно придёт, но без атрибута
`key_name`.

В сообщении назван адрес, а не подъезд, поэтому определить дверь нельзя:
событие попадает в сводную сущность адреса всегда, а в сущность домофона —
только если домофон единственный на адресе.

Уведомление в Telegram:

```yaml
triggers:
  - trigger: state
    entity_id: event.moy_dom_doorofon_access
conditions:
  - condition: template
    value_template: >-
      {{ trigger.to_state.attributes.get('event_type') == 'key_activated' }}
actions:
  - action: notify.telegram
    data:
      message: >-
        {% set who = trigger.to_state.attributes.get('key_name')
           if trigger is defined and trigger.to_state is defined else none %}
        {{ who ~ ' открыл домофон' if who else 'Кто-то открыл домофон ключом' }}
```

Триггер смотрит на **любое** изменение сущности, а тип события проверяется
условием. Так нужно, потому что у сущности события `state` — это время
события, а `event_type` лежит в атрибутах. Триггер с
`attribute: event_type` и `to: key_activated` кажется естественнее, но
сработает только один раз: HA пропускает срабатывание, когда значение
атрибута не изменилось, а два прохода подряд дают одно и то же значение
`key_activated`. Первое уведомление придёт, второе — уже нет.

Три особенности шаблона, все проверены рендерингом:

- условие смотрит `trigger.to_state.attributes`, а не `trigger.event.data`:
  объекта `event` у триггера `state` нет вовсе;
- проверка `trigger is defined and trigger.to_state is defined` нужна, чтобы
  шаблон не падал при ручном запуске. Кнопка «Run» у автоматизации
  подставляет `{"platform": None}`, а «Выполнить действие» в редакторе скрипта
  не подставляет `trigger` вовсе. Без проверки в обоих случаях будет
  `UndefinedError`;
- вызов сервиса уведомления зависит от вашей интеграции Telegram. Здесь
  показан `notify.telegram`; для `telegram_mtproxy` это
  `telegram_mtproxy.send_message` с `entity_id` целевого `notify`-объекта.

Если оператор перестанет писать имя в текст, `key_name` станет пустым, а
событие продолжит приходить анонимным. Признак виден в логе:
`resolved=NO_LABEL_MATCH`.

## Автоматизации

Звонок с порога как триггер:

```yaml
triggers:
  - trigger: state
    entity_id: event.moy_dom_doorbell
conditions:
  - condition: template
    value_template: >-
      {{ trigger.to_state.attributes.get('event_type') == 'ring' }}
actions:
  - action: notify.mobile_app_phone
    data:
      message: "Звонок в домофон"
  - action: my_dom_ru.answer
```

Условие тоже обязательно: у сущности события `state` — это время события, а не
`on`, поэтому триггер ловит любое изменение, а `ring` отсекается условием.

Автоматическое открытие двери гостю по пропуску — по вашему усмотрению и
возможностям домофона: интеграция даёт сущность `lock`, а правило открытия
остаётся в HA.

### Диагностика событий доступа

Если проход по ключу не появился, включите отладку и откройте дверь ключом:

```yaml
# configuration.yaml — затем перезапуск и «Параметры → Журналы → Отладка»
logger:
  default: warning
  logs:
    custom_components.my_dom_ru: debug
```

Появится четыре вида записей:

- `History poll ok: N events` — поллер достучался до облака;
- `History event … backend_type=accessKeyActivated source=<тип>:<id>` — событие
  пришло; здесь видно, какой `source` прислал оператор. Он нужен, если
  событие пришло, но не отнесено ни к одному домофону;
- `Key activation … resolved=Иван` либо `resolved=NO_LABEL_MATCH` — сработало
  ли сопоставление имён;
- `FCM: key activation …` — та же информация из realtime-пуша. Если этой строки
  нет, а `History event` есть, значит push-канал не работает и придётся ждать
  опроса.

Текст события оператора в лог не пишется: в нём содержится код ключа, а
`home-assistant.log` часто прикладывают к issue. В лог попадает только
разрешённое имя.

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
