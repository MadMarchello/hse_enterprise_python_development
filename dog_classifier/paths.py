"""Общие пути проекта: корень репозитория, чекпоинт, датасет."""

import os
from pathlib import Path

from dotenv import load_dotenv

# dog_classifier/paths.py -> parent = dog_classifier/, parent.parent = корень репо
REPO_ROOT = Path(__file__).resolve().parent.parent

# Веса лежат в artifacts/ в корне репозитория — независимо от cwd запуска.
CHECKPOINT_PATH = REPO_ROOT / "artifacts" / "dog_breeds_v2.pth"


def get_data_dir() -> Path:
    """Директория датасета: DOG_DATA_DIR из .env, иначе data/ в корне репо."""
    load_dotenv(REPO_ROOT / ".env")
    return Path(os.getenv("DOG_DATA_DIR", REPO_ROOT / "data"))
