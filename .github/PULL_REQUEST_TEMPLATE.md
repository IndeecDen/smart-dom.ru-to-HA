name: Pull request
description: Изменение в интеграции «Умный Дом.ру»
body:
  - type: markdown
    attributes:
      value: |
        Перед отправкой прочитайте [CONTRIBUTING.md](../blob/main/CONTRIBUTING.md):
        правила кода, проверки и требования к безопасности. Секреты, HAR-записи,
        APK и персональные данные в pull request не прикладываются.

  - type: input
    id: summary
    attributes:
      label: Что изменено
    validations:
      required: true

  - type: input
    id: motivation
    attributes:
      label: Зачем
      description: Ссылка на issue или описание проблемы.
    validations:
      required: true

  - type: dropdown
    id: verification
    attributes:
      label: Как проверено
      options:
        - Только unit-тесты
        - Прогон tests/unit, tests/ha, tests/portable
        - Полный pytest tests/ на Linux CI
        - Проверено на своём аккаунте и адресе
        - Не проверялось
    validations:
      required: true

  - type: textarea
    id: checklist
    attributes:
      label: Чеклист
      value: |
        - [ ] Секреты не попали в код, логи и тестовые данные
        - [ ] Новый шаг config flow отражён в strings.json и translations/ru.json, translations/en.json
        - [ ] Тесты добавлены или обновлены под изменение
        - [ ] Документация обновлена, если изменилось поведение
        - [ ] CHANGELOG.md содержит запись об изменении
    validations:
      required: true
