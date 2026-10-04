from homework.report import build_report, format_value_block, sample_values, types_report


def test_sample_values_has_all_eight_types():
    types = {type(value) for value in sample_values()}
    assert types == {int, float, bool, str, list, tuple, set, dict}


def test_types_report_format():
    report = types_report()
    assert report == (
        "Отчет по первой лабораторной работе:\n"
        "Демонстрация встроенных типов данных Python\n"
        "\n"
        "- Тип: <class 'int'>\n"
        "- Значение: 42\n"
        "------------------\n"
        "- Тип: <class 'float'>\n"
        "- Значение: 3.14\n"
        "------------------\n"
        "- Тип: <class 'bool'>\n"
        "- Значение: True\n"
        "------------------\n"
        "- Тип: <class 'str'>\n"
        "- Значение: python\n"
        "------------------\n"
        "- Тип: <class 'list'>\n"
        "- Значение: [1, 2, 3]\n"
        "------------------\n"
        "- Тип: <class 'tuple'>\n"
        "- Значение: ('a', 'b')\n"
        "------------------\n"
        "- Тип: <class 'set'>\n"
        "- Значение: {1, 2, 3}\n"
        "------------------\n"
        "- Тип: <class 'dict'>\n"
        "- Значение: {'course': 'python', 'homework': 1}\n"
        "------------------"
    )


def test_build_report_prepends_full_name():
    full_name = "Иванов Иван Иванович"
    report = build_report(full_name)
    assert report == f"ФИО: {full_name}\n\n{types_report()}"


def test_build_report_empty_name_has_no_extra_line():
    report = build_report("")
    assert report == types_report()
    assert not report.startswith("ФИО:")


def test_string_set_formatted_stably():
    value = {"python", "course", "homework"}
    assert "- Значение: {'course', 'homework', 'python'}" in format_value_block(value)
