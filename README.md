# hse_enterprise_python_development

Два пакета в одном репозитории (монорепо):

- `report_mailer/` — Homework 01: отчёт по типам Python, MD5/SHA-256, отправка письма через Яндекс SMTP.
- `dog_classifier/` — Homework 02: распознавание породы собаки (ResNet18 + Oxford-IIIT Pet).

## Установка

Через uv (воркспейс из корневого `pyproject.toml`):

```bash
cd hse_enterprise_python_development
uv sync
```

Или через pip в одно виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ./report_mailer -e ./dog_classifier
```

Флаг `-e` (editable) ставит оба пакета «в разработку»:
правите код — изменения сразу видны без переустановки.
