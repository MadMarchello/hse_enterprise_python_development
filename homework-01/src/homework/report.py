def sample_values():
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


def _format_value(value) -> str:
    if isinstance(value, set):
        items = ", ".join(repr(item) for item in sorted(value, key=repr))
        return f"{{{items}}}"
    return str(value)


def format_typed_line(value) -> str:
    return f"{_format_value(value)} {type(value)}"


def build_report(full_name: str) -> str:
    report = "\n".join(format_typed_line(value) for value in sample_values())
    if not full_name:
        return report
    return f"{report}\n{full_name}"
