"""Модель: ResNet-18 с заменённой последней линейкой (fc) под наши классы."""

from pathlib import Path

import torch
from torch import nn
from torchvision.models import ResNet18_Weights, resnet18


def get_device() -> torch.device:
    """Выбрать устройство: Apple Silicon (mps), иначе CPU."""
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def get_transform():
    """Стандартный препроцессинг ResNet-18: resize/crop/нормализация -> тензор."""
    return ResNet18_Weights.DEFAULT.transforms()


def build_model(num_classes: int, pretrained: bool = True) -> nn.Module:
    """Создать ResNet-18 и заменить голову fc под num_classes классов.

    Веса backbone замораживаем (requires_grad=False) — обучается
    только новый слой fc. Это transfer learning.
    """
    weights = ResNet18_Weights.DEFAULT if pretrained else None
    model = resnet18(weights=weights)

    for p in model.parameters():
        p.requires_grad = False

    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def save_checkpoint(
    model: nn.Module,
    classes: list[str],
    epoch_losses: list[float],
    checkpoint_path: Path,
) -> None:
    """Сохранить веса модели и метаданные в один .pth-файл."""
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state": model.state_dict(),
            "classes": classes,
            "epoch_losses": epoch_losses,
        },
        checkpoint_path,
    )


def load_checkpoint(
    checkpoint_path: Path,
    device: torch.device,
) -> tuple[nn.Module, list[str], list[float]]:
    """Загрузить чекпоинт: вернуть (модель, список классов, loss по эпохам)."""
    try:
        checkpoint = torch.load(
            checkpoint_path,
            map_location=device,
            weights_only=False,
        )
    except TypeError:  # старые версии torch без аргумента weights_only
        checkpoint = torch.load(checkpoint_path, map_location=device)

    classes = checkpoint["classes"]
    epoch_losses = checkpoint["epoch_losses"]

    # Важно: создаём модель БЕЗ pretrained-весов — они всё равно
    # будут перезаписаны значениями из чекпоинта.
    model = build_model(num_classes=len(classes), pretrained=False)
    model.load_state_dict(checkpoint["model_state"])
    model = model.to(device)
    model.eval()
    return model, classes, epoch_losses
