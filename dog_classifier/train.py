"""Обучение модели.

Запуск из корня репозитория:
    python -m dog_classifier.train --epochs 5
    python -m dog_classifier.train --epochs 1 --limit 256 \
        --checkpoint artifacts/smoke.pth   # быстрая проверка
"""

import argparse
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, Subset

from .dataset import CLASSES, build_dataloaders
from .model import build_model, get_device, get_transform, save_checkpoint
from .paths import CHECKPOINT_PATH, get_data_dir


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    epochs: int,
) -> list[float]:
    """Один полный цикл обучения; возвращает loss последнего батча каждой эпохи."""
    epoch_losses: list[float] = []
    for epoch in range(epochs):
        model.train()  # режим обучения (важно для dropout/batchnorm)
        for X, y in train_loader:
            X = X.to(device)
            y = y.to(device)

            optimizer.zero_grad()        # обнулить градиенты прошлого шага
            logits = model(X)            # прямой проход
            loss = criterion(logits, y)  # посчитать ошибку
            loss.backward()              # обратный проход: градиенты
            optimizer.step()             # шаг оптимизатора

        epoch_losses.append(loss.item())
        print(f"epoch={epoch + 1} loss={loss.item():.4f}")
    return epoch_losses


def evaluate(
    model: nn.Module,
    test_loader: DataLoader,
    device: torch.device,
) -> tuple[float, list[int], list[int]]:
    """Посчитать accuracy на test: общую и по каждому классу."""
    model.eval()  # режим инференса
    correct = 0
    total = 0
    correct_by_class = [0] * len(CLASSES)
    total_by_class = [0] * len(CLASSES)

    with torch.no_grad():  # градиенты не нужны — быстрее и меньше память
        for X, y in test_loader:
            X = X.to(device)
            y = y.to(device)

            logits = model(X)
            pred = logits.argmax(dim=1)
            match = pred == y

            correct += match.sum().item()
            total += y.size(0)

            for class_id in range(len(CLASSES)):
                mask = y == class_id
                total_by_class[class_id] += mask.sum().item()
                correct_by_class[class_id] += (match & mask).sum().item()

    accuracy = correct / total
    return accuracy, correct_by_class, total_by_class


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="обучаться только на первых N примерах train (0 = все)",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=CHECKPOINT_PATH,
        help="куда сохранить чекпоинт",
    )
    args = parser.parse_args()

    device = get_device()
    print("device:", device)

    transform = get_transform()
    train_loader, test_loader, class_weights = build_dataloaders(
        get_data_dir(), transform, batch_size=args.batch_size
    )

    if args.limit > 0:  # режим быстрой проверки кода
        subset = Subset(train_loader.dataset, range(args.limit))
        train_loader = DataLoader(
            subset, batch_size=args.batch_size, shuffle=True
        )
        print(f"режим проверки: только {args.limit} примеров train")

    model = build_model(num_classes=len(CLASSES), pretrained=True)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights.to(device))
    optimizer = torch.optim.SGD(model.fc.parameters(), lr=0.01, momentum=0.9)

    epoch_losses = train_model(
        model, train_loader, criterion, optimizer, device, args.epochs
    )

    accuracy, correct_by_class, total_by_class = evaluate(
        model, test_loader, device
    )
    print(f"\naccuracy = {accuracy:.2%}")
    for name, ok, n in zip(CLASSES, correct_by_class, total_by_class):
        print(f"{name:<28} {ok / n:.2%}  ({ok}/{n})")

    save_checkpoint(model, CLASSES, epoch_losses, args.checkpoint)
    print("сохранено:", args.checkpoint.resolve())


if __name__ == "__main__":
    main()
