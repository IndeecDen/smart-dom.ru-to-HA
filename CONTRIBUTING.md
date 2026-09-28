# Contributing

Спасибо за интерес к интеграции. Это неофициальный проект, он не связан с
ЭР-Телеком и опирается на закрытое облако оператора.

## Безопасность прежде всего

Не присылайте в issues, pull request и трейсах:

- пароли, коды из SMS, access/refresh-токены, заголовки с `Bearer`;
- коды электронных ключей и ссылки временных пропусков;
- HAR-записи, APK/APKM, декомпилированный код приложения, экспорт `.storage`;
- полные логи Home Assistant и персональные данные гостей.

Для диагностики используйте кнопку «Загрузить диагностику» в UI интеграции:
она редактирует секреты. В описании проблемы укажите версию HA, способ
установки, шаг воспроизведения и код HTTP.

## Окружение

```powershell
uv venv .venv-ha --python 3.14
.venv-ha/Scripts/python.exe -m pip install -r requirements_test.txt
npm ci --prefix frontend
```

## Проверки перед коммитом

Полный набор — в [docs/TESTING.md](docs/TESTING.md). Кратко:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.venv-ha/Scripts/python.exe -m pytest -p pytest_asyncio.plugin tests/unit tests/ha tests/portable -q
npm run typecheck --prefix frontend
npm test --prefix frontend
npm run build --prefix frontend
.venv/Scripts/python.exe tools/copy_licenses.py
.venv/Scripts/python.exe tools/package.py
```

Полный `pytest tests/` рассчитан на Linux: плагин
`pytest-homeassistant-custom-component` не работает на Windows из-за
отсутствующего `fcntl`. В CI он прогоняется на
[ubuntu-latest](.github/workflows/ci.yml).

## Правила кода

- Стиль и соглашения — как в HA core: `ruff`, асинхронный код, типизация
  публичных методов.
- Логирование только через `%`-форматирование, **никогда** f-string внутри
  `LOGGER.*()`.
- Секреты в логи не попадают — используйте `_logging.redact` и
  `SENSITIVE_KEYS`.
- `unique_id` сущностей стабильны и не содержат локализованных строк.
- Новый шаг config flow требует строки в `strings.json` и
  `translations/ru.json` + `translations/en.json`.
- Версия config entry повышается только через `async_migrate_entry`.
- Тесты не подгоняются под сломанное поведение: сначала воспроизведите дефект.

## Контракты API

`docs/apk-api-9.10.0.json` — каталог наблюдавшихся деклараций из профиля
приложения 9.10.0. Он описывает совместимость, а не гарантию: наличие
endpoint в приложении не доказывает его доступность в вашем тарифе.
Обновления каталога — через `tools/extract_api_contracts.py`.

## Коммит и релиз

- Версия живёт в `custom_components/my_dom_ru/manifest.json` и
  `frontend/package.json`; архивы собирает `tools/package.py` по явному
  allowlist файлов.
- Релиз: тег `v<версия>`, `CHANGELOG.md` обновлён, архивы
  `my_dom_ru.zip` (для HACS) и `my_dom_ru-<версия>-manual.zip` приложены к
  GitHub Release, `dist/SHA256SUMS.txt` соответствует приложенным файлам.
- Коммиты и issue — на русском или английском, коротко и по делу.

## Проверка на реальном устройстве

Любое утверждение «работает у меня» с открытием двери, живым звонком,
пропуском или ключом проверяйте только на собственном аккаунте и адресе и
указывайте это в issue. Общее тестовое окружение оператора недоступно.
