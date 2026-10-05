"""Датасет: обёртка над Oxford-IIIT Pet.

Оставляем 25 пород собак, всё остальное (кошки и прочие породы)
помечаем классом «другие».
"""

from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets

BREEDS = [
    "American Bulldog",
    "American Pit Bull Terrier",
    "Basset Hound",
    "Beagle",
    "Boxer",
    "Chihuahua",
    "English Cocker Spaniel",
    "English Setter",
    "German Shorthaired",
    "Great Pyrenees",
    "Havanese",
    "Japanese Chin",
    "Keeshond",
    "Leonberger",
    "Miniature Pinscher",
    "Newfoundland",
    "Pomeranian",
    "Pug",
    "Saint Bernard",
    "Samoyed",
    "Scottish Terrier",
    "Shiba Inu",
    "Staffordshire Bull Terrier",
    "Wheaten Terrier",
    "Yorkshire Terrier",
]
OTHER_NAME = "другие"
CLASSES = BREEDS + [OTHER_NAME]
OTHER_ID = len(BREEDS)  # индекс класса «другие» = 25


def build_label_mapping(base_classes: list[str]) -> dict[int, int]:
    """Собрать словарь {старый индекс класса -> новый индекс 0..24}.

    В исходном датасете 37 классов (и кошки, и собаки), а нам нужны
    только 25 пород собак. Классы вне списка в словарь не попадают —
    их поймает .get(..., OTHER_ID) в to_new_label.
    """
    name_to_old = {name: i for i, name in enumerate(base_classes)}
    selected_old = [name_to_old[name] for name in BREEDS]
    return {old: new for new, old in enumerate(selected_old)}


def to_new_label(old_y: int, old_to_new: dict[int, int]) -> int:
    """Перевести старый индекс класса в новый; неизвестные -> «другие»."""
    return old_to_new.get(old_y, OTHER_ID)


class BreedsWithOther(Dataset):
    """Свой Dataset-класс: обязаны быть __len__ и __getitem__.

    DataLoader спрашивает у объекта len(dataset) и dataset[i] —
    больше PyTorch от датасета ничего не требует.
    """

    def __init__(self, base: Dataset, transform, old_to_new: dict[int, int]):
        self.base = base            # исходный OxfordIIITPet
        self.transform = transform  # препроцессинг картинки -> тензор
        self.old_to_new = old_to_new

    def __len__(self) -> int:
        """Сколько всего примеров в датасете."""
        return len(self.base)

    def __getitem__(self, i: int) -> tuple[torch.Tensor, int]:
        """Вернуть один пример: (тензор картинки, новый номер класса)."""
        image, old_y = self.base[i]
        image = self.transform(image)
        return image, to_new_label(old_y, self.old_to_new)


def load_base_datasets(data_dir: Path) -> tuple[Dataset, Dataset]:
    """Загрузить trainval и test части Oxford-IIIT Pet."""
    train_all = datasets.OxfordIIITPet(
        root=data_dir,
        split="trainval",
        target_types="category",
        download=True,
    )
    test_all = datasets.OxfordIIITPet(
        root=data_dir,
        split="test",
        target_types="category",
        download=True,
    )
    return train_all, test_all


def compute_class_weights(train_all: Dataset, old_to_new: dict[int, int]) -> torch.Tensor:
    """Веса классов для CrossEntropyLoss: редкий класс -> больший вес."""
    label_counts = [0] * len(CLASSES)
    for old_y in train_all._labels:
        label_counts[to_new_label(old_y, old_to_new)] += 1
    total_labels = sum(label_counts)
    return torch.tensor(
        [total_labels / (len(CLASSES) * count) for count in label_counts],
        dtype=torch.float32,
    )


def build_dataloaders(
    data_dir: Path,
    transform,
    batch_size: int = 32,
) -> tuple[DataLoader, DataLoader, torch.Tensor]:
    """Собрать train/test DataLoader'ы и веса классов одной функцией."""
    train_all, test_all = load_base_datasets(data_dir)
    old_to_new = build_label_mapping(train_all.classes)

    train_ds = BreedsWithOther(train_all, transform, old_to_new)
    test_ds = BreedsWithOther(test_all, transform, old_to_new)

    class_weights = compute_class_weights(train_all, old_to_new)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader, class_weights
