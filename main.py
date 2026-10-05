"""Точка входа проекта: Homework 03.

Весь рабочий код лежит в пакете dog_classifier/ (dataset, model,
train, predict, homework_tasks) — здесь мы его только импортируем
и запускаем.

Запуск из корня репозитория:
    python main.py                  # задачи 1–3 + предсказание по демо-фото
    python main.py путь/к/фото.jpg  # задачи 1–3 + предсказание по своему фото

Обучение запускается отдельно:
    python -m dog_classifier.train --epochs 5
"""

import sys
from pathlib import Path

from PIL import Image

from dog_classifier.homework_tasks import run_all as run_homework_tasks
from dog_classifier.model import get_device, get_transform, load_checkpoint
from dog_classifier.paths import CHECKPOINT_PATH, get_data_dir
from dog_classifier.predict import predict, show_probabilities


def main() -> None:
    # Задачи 1–3: shape тензора, print(model), алиасы и копии списков.
    run_homework_tasks()

    # Задача «инференс»: предсказание по готовому чекпоинту.
    print("=" * 60)
    print("ПРЕДСКАЗАНИЕ ПО ФОТОГРАФИИ")
    print("=" * 60)

    device = get_device()
    transform = get_transform()
    model, classes, _ = load_checkpoint(CHECKPOINT_PATH, device)
    print("device:", device)
    print("классов:", len(classes))

    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
    else:  # демо-режим: бигль из датасета
        image_path = (
            get_data_dir() / "oxford-iiit-pet" / "images" / "Beagle_1.jpg"
        )

    if not image_path.is_file():
        raise FileNotFoundError(f"Нет файла {image_path.resolve()}")

    print("фото:", image_path.resolve())
    image = Image.open(image_path).convert("RGB")
    class_id, probabilities = predict(image, model, transform, device)
    show_probabilities(class_id, probabilities, classes)


if __name__ == "__main__":
    main()
