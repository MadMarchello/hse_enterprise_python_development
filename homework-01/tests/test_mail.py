from email import message_from_string
from unittest.mock import MagicMock, patch

from homework.mail import format_result_body, send_email


def test_format_result_body_contains_name_and_hashes():
    body = format_result_body("Иванов Иван Иванович", "md5digest", "sha256digest")
    assert body == (
        "ФИО: Иванов Иван Иванович\n"
        "\n"
        "MD5:\n"
        "md5digest\n"
        "\n"
        "SHA-256:\n"
        "sha256digest"
    )


@patch("homework.mail.smtplib.SMTP_SSL")
def test_send_email_logs_in_and_sends_without_network(mock_smtp_ssl):
    server = MagicMock()
    mock_smtp_ssl.return_value.__enter__.return_value = server

    send_email(
        subject="Homework 01",
        body="result-body",
        to_email="to@example.com",
        from_email="from@yandex.ru",
        password="app-password",
    )

    mock_smtp_ssl.assert_called_once()
    host, port = mock_smtp_ssl.call_args.args[:2]
    assert host == "smtp.yandex.ru"
    assert port == 465
    assert "context" in mock_smtp_ssl.call_args.kwargs

    server.login.assert_called_once_with("from@yandex.ru", "app-password")
    server.sendmail.assert_called_once()
    from_email, to_email, payload = server.sendmail.call_args.args
    assert from_email == "from@yandex.ru"
    assert to_email == "to@example.com"
    msg = message_from_string(payload)
    assert msg["Subject"] == "Homework 01"
    assert msg["From"] == "from@yandex.ru"
    assert msg["To"] == "to@example.com"
    body_part = msg.get_payload()[0]
    assert body_part.get_payload(decode=True).decode("utf-8") == "result-body"
