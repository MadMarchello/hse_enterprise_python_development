# Changelog

## [Unreleased]

- Добавлен `report_ mailer/` — пакет домашки 01 (отчёт по типам, хеши, отправка письма) с тестами.
- Добавлен `dog_classifier/` — ноутбук с ML-моделью распознавания собак и условия задания.
- Структура репозитория разделена на два пакета: `report_ mailer` и `homework-02`.
- Добавлена новая структура хранения файлов + перенес ноутбука в main.py файл

## [0.2.0] - Homework 03

- Монолит `dog_classifier/main.py` (485 строк) разнесён по модулям пакета:
  `paths.py` (пути проекта), `dataset.py` (Dataset-класс `BreedsWithOther`
  с `__len__`/`__getitem__`, DataLoader'ы), `model.py` (сборка ResNet-18,
  заморозка backbone, чекпоинты), `train.py` (обучение и оценка),
  `predict.py` (инференс с type hints).
- Добавлен `dog_classifier/homework_tasks.py` — задачи 1–3 задания:
  shape тензора после transform и unsqueeze(0), разбор print(model)
  (conv1, layer1–layer4, avgpool, fc), алиасы vs копии списков.
- Добавлен `main.py` в корне репозитория — точка входа, импортирует
  пакет `dog_classifier` и запускает задачи 1–3 + предсказание по фото.
- Type hints добавлены к функциям пакета (`predict_image`, `train_model` и др.).
- Чекпоинт `artifacts/dog_breeds_v2.pth` подключён к пакету; `.env` задаёт
  `DOG_DATA_DIR` с расположением датасета Oxford-IIIT Pet.
- Добавлен отчёт `dog_classifier/docs/homework-03-отчёт.md` и сохранённые
  выводы запусков в `dog_classifier/docs/output/`.

## [0.1.0] - Homework 01

- Исходная версия: src-layout, отчёт по восьми типам, MD5/SHA-256, отправка письма через Яндекс SMTP.
