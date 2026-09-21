from collections.abc import Iterable
from typing import cast


def sample_values() -> list[object]:
    return [
        42,
        3.14,
        True,
        "python",
        [1, 2, 3],
        ("a", "b"),
        {3, 1, 2},
        {"course": "python", "homework": 1},
    ]


def _format_value(value: object) -> str:
    if isinstance(value, set):
        members = cast(Iterable[object], value)
        items = ", ".join(sorted(repr(item) for item in members))
        return f"{{{items}}}"
    return str(value)


def format_value_block(value: object) -> str:
    return (
        f"- Тип: {type(value)}\n"
        f"- Значение: {_format_value(value)}\n"
        f"------------------"
    )


def types_report() -> str:
    blocks = "\n".join(format_value_block(value) for value in sample_values())
    return (
        "Отчет по первой лабораторной работе:\n"
        "Демонстрация встроенных типов данных Python\n"
        "\n"
        f"{blocks}"
    )


def build_report(full_name: str) -> str:
    report = types_report()
    if not full_name:
        return report
    return f"ФИО: {full_name}\n\n{report}"
