# hse_enterprise_python_development

Два пакета в одном репозитории (монорепо):

- `report_mailer/` — Homework 01: отчёт по типам Python, MD5/SHA-256, отправка письма через Яндекс SMTP.
- `dog_classifier/` — Homework 02/03: распознавание породы собаки (ResNet18 + Oxford-IIIT Pet).
  Пакет из модулей `dataset / model / train / predict`; точка входа — `main.py`
  в корне репозитория (`python main.py`), обучение — `python -m dog_classifier.train`.

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

## Настройка .env

Оба пакета читают `.env` из корня репозитория:

```bash
cp .env.example .env
```

- `DOG_DATA_DIR` — внешняя папка для датасета Oxford-IIIT Pet (~800 МБ).
  Без неё датасет ляжет в `data/` в корне репо.
- `FULL_NAME`, `YANDEX_EMAIL`, `YANDEX_APP_PASSWORD`, `TO_EMAIL` —
  параметры для `report_mailer`. Без них программа спросит ФИО, email
  и пароль в консоли (пароль — скрытый ввод через `getpass`).
  Обычный пароль Яндекса не подойдёт, нужен
  [пароль приложения](https://id.yandex.ru/security/app-passwords).

Файл `.env` в Git не попадает (есть в `.gitignore`).
