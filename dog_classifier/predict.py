"""Инференс: фото -> порода.

Запуск из корня репозитория:
    python -m dog_classifier.predict путь/к/фото.jpg
    python -m dog_classifier.predict   # демо: Beagle_1.jpg из датасета
"""

import sys
from pathlib import Path

import torch
from PIL import Image
from torch import nn

from .model import get_device, get_transform, load_checkpoint
from .paths import CHECKPOINT_PATH, get_data_dir


def predict(
    image: Image.Image,
    model: nn.Module,
    transform,
    device: torch.device,
) -> tuple[int, torch.Tensor]:
    """Предсказать класс одной картинки.

    Возвращает (номер класса, тензор вероятностей по всем классам).
    """
    x = transform(image)            # PIL-картинка -> тензор [3, 224, 224]
    x = x.unsqueeze(0).to(device)   # добавить batch-размерность -> [1, 3, 224, 224]
    with torch.no_grad():
        logits = model(x)
        probabilities = torch.softmax(logits, dim=1)
    class_id = probabilities.argmax(dim=1).item()
    return class_id, probabilities[0]


def predict_image(
    image_path: str,
    model: nn.Module,
    classes: list[str],
    transform,
    device: torch.device,
) -> tuple[str, float]:
    """Обёртка «путь к файлу -> (имя класса, уверенность)»."""
    image = Image.open(image_path).convert("RGB")
    class_id, probabilities = predict(image, model, transform, device)
    return classes[class_id], probabilities[class_id].item()


def show_probabilities(
    class_id: int,
    probabilities: torch.Tensor,
    classes: list[str],
) -> None:
    """Красиво напечатать предсказание и вероятности всех классов."""
    print(classes[class_id], f"{probabilities[class_id].item():.1%}")
    print()
    for name, probability in zip(classes, probabilities.tolist()):
        print(f"{name:<28} {probability:.1%}")


def main() -> None:
    device = get_device()
    transform = get_transform()

    model, classes, _ = load_checkpoint(CHECKPOINT_PATH, device)
    print("device:", device)
    print("классов:", len(classes))

    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
    else:  # демо-режим: возьмём бигля из датасета
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
