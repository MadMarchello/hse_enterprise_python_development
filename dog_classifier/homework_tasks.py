"""Задачи 1–3 домашнего задания 03.

1. shape тензора после transform и после unsqueeze(0).
2. print(model) и поиск conv1, layer1..layer4, avgpool, fc.
3. Два имени одного объекта vs копия списка (на примере list).
"""

from PIL import Image

from .model import build_model, get_transform
from .paths import get_data_dir


def task1_shapes() -> None:
    print("=" * 60)
    print("ЗАДАЧА 1. shape после transform и после unsqueeze(0)")
    print("=" * 60)

    image_path = (
        get_data_dir() / "oxford-iiit-pet" / "images" / "Beagle_1.jpg"
    )
    transform = get_transform()
    image = Image.open(image_path).convert("RGB")
    print("исходная PIL-картинка:", image.size, image.mode)

    x = transform(image)
    print("shape после transform:   ", tuple(x.shape))

    x = x.unsqueeze(0)
    print("shape после unsqueeze(0):", tuple(x.shape))
    print()


def task2_model() -> None:
    print("=" * 60)
    print("ЗАДАЧА 2. print(model): conv1, layer1..layer4, avgpool, fc")
    print("=" * 60)

    model = build_model(num_classes=26, pretrained=False)
    print(model)
    print()

    # Те же блоки можно достать как атрибуты объекта:
    print("model.conv1   ->", model.conv1)
    print("model.layer1  ->", type(model.layer1).__name__,
          f"({len(model.layer1)} блока BasicBlock)")
    print("model.layer2  ->", type(model.layer2).__name__,
          f"({len(model.layer2)} блока)")
    print("model.layer3  ->", type(model.layer3).__name__,
          f"({len(model.layer3)} блока)")
    print("model.layer4  ->", type(model.layer4).__name__,
          f"({len(model.layer4)} блока)")
    print("model.avgpool ->", model.avgpool)
    print("model.fc      ->", model.fc)
    print()


def task3_list_alias_vs_copy() -> None:
    print("=" * 60)
    print("ЗАДАЧА 3. Два имени одного списка vs копия списка")
    print("=" * 60)

    # 1) y = x — это НЕ копия, а второе имя того же объекта
    x = [1, 2, 3]
    y = x
    print("x =", x, " id(x) =", id(x))
    print("y =", y, " id(y) =", id(y), " <- тот же id, объект один")

    y.append(4)
    print("после y.append(4): x =", x, " <- x тоже изменился!")
    print()

    # 2) z = x.copy() — настоящая (поверхностная) копия
    x = [1, 2, 3]
    z = x.copy()
    print("x =", x, " id(x) =", id(x))
    print("z =", z, " id(z) =", id(z), " <- другой id, объектов два")

    z.append(4)
    print("после z.append(4): x =", x, " <- x не изменился")
    print("                  z =", z)


def run_all() -> None:
    """Запустить все три задачи подряд."""
    task1_shapes()
    task2_model()
    task3_list_alias_vs_copy()


if __name__ == "__main__":
    run_all()
