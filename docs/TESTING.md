# Воспроизводимые проверки и пределы

Рабочая среда на момент сборки — Windows, Python 3.14.7 с Home Assistant
2026.9.0b6. Архивный базовый проект ориентирован на HA 2026.8.1+.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.venv-ha/Scripts/python.exe -m pytest -p pytest_asyncio.plugin tests/unit tests/ha -q
.venv-ha/Scripts/python.exe -m pytest -p pytest_asyncio.plugin tests/portable -q
npm test --prefix frontend
npm run typecheck --prefix frontend
npm run build --prefix frontend
.venv/Scripts/python.exe tools/package.py
```

Локально проверены контракты 9.10.0, валидация и область аккаунта, регистрация
действий в настоящем объекте Home Assistant, refresh токена и отсутствие
повтора небезопасных команд, SIP-протокол, карточки и типы. Тесты из `tests/upstream`
сохранены как регрессия для Linux CI; плагин `pytest-homeassistant-custom-component`
на Windows не запускается из-за отсутствующего системного модуля `fcntl`.
Проверка у реального оператора не проводилась: нет входа в аккаунт и домофона.

Перед стабильным релизом нужно прогнать весь `pytest tests/` на Linux,
затем на своём адресе проверить вход, refresh, снимок/поток, один физический
звонок, ответ/отбой, открыть дверь, срок действия пропуска, список ключей,
настройки поддерживаемой камеры и обращение. Для тестирования сети используйте
только собственный аккаунт, не размещайте HAR, APK, токены и данные гостя в
публичном репозитории.
