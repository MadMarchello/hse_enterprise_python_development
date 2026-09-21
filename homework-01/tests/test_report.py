from homework.report import _format_value, build_report, format_typed_line, sample_values


def test_sample_values_has_all_eight_types():
    types = {type(value) for value in sample_values()}
    assert types == {int, float, bool, str, list, tuple, set, dict}


def test_build_report_appends_full_name():
    full_name = "Иванов Иван Иванович"
    report = build_report(full_name)
    typed_lines = [format_typed_line(value) for value in sample_values()]
    assert report == "\n".join(typed_lines) + f"\n{full_name}"
    assert report.endswith(full_name)


def test_build_report_empty_name_has_no_extra_line():
    report = build_report("")
    typed_lines = [format_typed_line(value) for value in sample_values()]
    assert report == "\n".join(typed_lines)
    assert not report.endswith("\n")


def test_string_set_formatted_stably():
    value = {"python", "course", "homework"}
    expected = "{'course', 'homework', 'python'}"
    assert _format_value(value) == expected
    assert format_typed_line(value).startswith(expected + " ")
