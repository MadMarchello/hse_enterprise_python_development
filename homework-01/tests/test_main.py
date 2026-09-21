from unittest.mock import patch

from homework.main import main


@patch("homework.main.send_email")
@patch("homework.main.calculate_hashes", return_value=("md5digest", "sha256digest"))
@patch("homework.main.build_report", return_value="report-text")
@patch("homework.main.load_dotenv", return_value=True)
def test_main_uses_env_variables(mock_load_dotenv, mock_build_report, mock_hashes, mock_send_email):
    env = {
        "FULL_NAME": "Иванов Иван Иванович",
        "YANDEX_EMAIL": "from@yandex.ru",
        "YANDEX_APP_PASSWORD": "app-password",
        "TO_EMAIL": "to@edu.hse.ru",
    }
    with (
        patch.dict("os.environ", env, clear=False),
        patch("homework.main.input") as mock_input,
        patch("homework.main.getpass") as mock_getpass,
    ):
        main()

    mock_load_dotenv.assert_called_once()
    mock_input.assert_not_called()
    mock_getpass.assert_not_called()
    mock_build_report.assert_called_once_with("Иванов Иван Иванович")
    mock_hashes.assert_called_once_with("report-text")
    mock_send_email.assert_called_once()
    sent = mock_send_email.call_args.kwargs
    assert sent["subject"] == "Homework 01"
    assert sent["to_email"] == "to@edu.hse.ru"
    assert sent["from_email"] == "from@yandex.ru"
    assert sent["password"] == "app-password"
    assert "Иванов Иван Иванович" in sent["body"]
    assert "md5digest" in sent["body"]
    assert "sha256digest" in sent["body"]


@patch("homework.main.send_email")
@patch("homework.main.calculate_hashes", return_value=("md5digest", "sha256digest"))
@patch("homework.main.build_report", return_value="report-text")
@patch("homework.main.load_dotenv", return_value=True)
def test_main_prompts_when_email_password_and_name_are_empty(
    mock_load_dotenv, mock_build_report, mock_hashes, mock_send_email
):
    env = {
        "FULL_NAME": "",
        "YANDEX_EMAIL": "",
        "YANDEX_APP_PASSWORD": "",
        "TO_EMAIL": "to@edu.hse.ru",
    }
    with (
        patch.dict("os.environ", env, clear=False),
        patch("homework.main.input", side_effect=["Петров Пётр", "from@yandex.ru"]) as mock_input,
        patch("homework.main.getpass", return_value="typed-password") as mock_getpass,
    ):
        main()

    mock_load_dotenv.assert_called_once()
    assert mock_input.call_count == 2
    mock_getpass.assert_called_once()
    mock_build_report.assert_called_once_with("Петров Пётр")
    mock_hashes.assert_called_once_with("report-text")
    sent = mock_send_email.call_args.kwargs
    assert sent["from_email"] == "from@yandex.ru"
    assert sent["password"] == "typed-password"
    assert sent["to_email"] == "to@edu.hse.ru"
