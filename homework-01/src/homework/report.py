def build_report() -> str:
    values = [
        42,
        3.14,
        True,
        "python",
        [1, 2, 3],
        ("a", "b"),
        {3, 1, 2},
        {"course": "python", "homework": 1},
    ]
    return "\n".join(f"{value} {type(value)}" for value in values)
