from email import message_from_string
from unittest.mock import patch

from homework.mail import format_result_body, send_email


def test_format_result_body_contains_name_hashes_and_types_report():
    types_section = (
        "Отчет по первой лабораторной работе:\n"
        "Демонстрация встроенных типов данных Python\n"
        "\n"
        "- Тип: <class 'int'>\n"
        "- Значение: 42\n"
        "------------------"
    )
    body = format_result_body(
        "Иванов Иван Иванович",
        "md5digest",
        "sha256digest",
        types_section,
    )
    assert body == (
        "ФИО: Иванов Иван Иванович\n"
        "MD5:md5digest\n"
        "SHA-256:sha256digest\n"
        "\n"
        f"{types_section}"
    )


class _FakeSMTP:
    def __init__(self) -> None:
        self.login_args: tuple[str, str] | None = None
        self.sent: tuple[str, str, str] | None = None

    def __enter__(self) -> "_FakeSMTP":
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    def login(self, user: str, password: str) -> None:
        self.login_args = (user, password)

    def sendmail(self, from_addr: str, to_addrs: str, msg: str) -> None:
        self.sent = (from_addr, to_addrs, msg)


def _text_body(raw: str) -> str:
    message = message_from_string(raw)
    for part in message.walk():
        if part.get_content_maintype() == "multipart":
            continue
        decoded = part.get_payload(decode=True)
        assert isinstance(decoded, bytes)
        return decoded.decode("utf-8")
    raise AssertionError("text part missing")


def test_send_email_logs_in_and_sends_without_network():
    servers: list[_FakeSMTP] = []
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fake_smtp(*args: object, **kwargs: object) -> _FakeSMTP:
        calls.append((args, kwargs))
        server = _FakeSMTP()
        servers.append(server)
        return server

    with patch("homework.mail.smtplib.SMTP_SSL", fake_smtp):
        send_email(
            subject="Homework 01",
            body="result-body",
            to_email="to@example.com",
            from_email="from@yandex.ru",
            password="app-password",
        )

    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[:2] == ("smtp.yandex.ru", 465)
    assert "context" in kwargs

    server = servers[0]
    assert server.login_args == ("from@yandex.ru", "app-password")
    assert server.sent is not None
    from_email, to_email, payload = server.sent
    assert from_email == "from@yandex.ru"
    assert to_email == "to@example.com"
    message = message_from_string(payload)
    assert message["Subject"] == "Homework 01"
    assert message["From"] == "from@yandex.ru"
    assert message["To"] == "to@example.com"
    assert _text_body(payload) == "result-body"
