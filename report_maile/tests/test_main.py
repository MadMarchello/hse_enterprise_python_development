from dataclasses import dataclass, field
from unittest.mock import patch

from homework.main import main


@dataclass
class _MainCalls:
    dotenv_calls: int = 0
    report_names: list[str] = field(default_factory=list)
    hashed: list[str] = field(default_factory=list)
    sent: list[dict[str, str]] = field(default_factory=list)
    input_prompts: list[str] = field(default_factory=list)
    input_answers: list[str] = field(default_factory=list)
    getpass_prompts: list[str] = field(default_factory=list)
    getpass_answer: str | None = None

    def load_dotenv(self, *_args: object, **_kwargs: object) -> bool:
        self.dotenv_calls += 1
        return True

    def build_report(self, full_name: str) -> str:
        self.report_names.append(full_name)
        return "report-text"

    def calculate_hashes(self, text: str) -> tuple[str, str]:
        self.hashed.append(text)
        return ("md5digest", "sha256digest")

    def send_email(
        self,
        *,
        subject: str,
        body: str,
        to_email: str,
        from_email: str,
        password: str,
        smtp_host: str = "smtp.yandex.ru",
        smtp_port: int = 465,
    ) -> None:
        del smtp_host, smtp_port
        self.sent.append(
            {
                "subject": subject,
                "body": body,
                "to_email": to_email,
                "from_email": from_email,
                "password": password,
            }
        )

    def read_input(self, prompt: str = "") -> str:
        self.input_prompts.append(prompt)
        if not self.input_answers:
            raise AssertionError(prompt)
        return self.input_answers.pop(0)

    def read_password(self, prompt: str = "", stream: object = None) -> str:
        del stream
        self.getpass_prompts.append(prompt)
        if self.getpass_answer is None:
            raise AssertionError(prompt)
        return self.getpass_answer


def _run_main(calls: _MainCalls, env: dict[str, str]) -> None:
    with (
        patch.dict("os.environ", env, clear=False),
        patch("homework.main.load_dotenv", calls.load_dotenv),
        patch("homework.main.build_report", calls.build_report),
        patch("homework.main.calculate_hashes", calls.calculate_hashes),
        patch("homework.main.send_email", calls.send_email),
        patch("homework.main.input", calls.read_input),
        patch("homework.main.getpass", calls.read_password),
    ):
        main()


def test_main_uses_env_variables():
    calls = _MainCalls()
    _run_main(
        calls,
        {
            "FULL_NAME": "Иванов Иван Иванович",
            "YANDEX_EMAIL": "from@yandex.ru",
            "YANDEX_APP_PASSWORD": "app-password",
            "TO_EMAIL": "to@edu.hse.ru",
        },
    )

    assert calls.dotenv_calls == 1
    assert calls.input_prompts == []
    assert calls.getpass_prompts == []
    assert calls.report_names == ["Иванов Иван Иванович"]
    assert calls.hashed == ["report-text"]
    assert len(calls.sent) == 1
    sent = calls.sent[0]
    assert sent["subject"] == "Homework 01"
    assert sent["to_email"] == "to@edu.hse.ru"
    assert sent["from_email"] == "from@yandex.ru"
    assert sent["password"] == "app-password"
    assert sent["body"].startswith(
        "ФИО: Иванов Иван Иванович\nMD5:md5digest\nSHA-256:sha256digest\n"
    )
    assert "Отчет по первой лабораторной работе:" in sent["body"]
    assert "- Тип:" in sent["body"]
    assert "- Значение:" in sent["body"]


def test_main_prompts_when_email_password_and_name_are_empty():
    calls = _MainCalls(
        input_answers=["Петров Пётр", "from@yandex.ru"],
        getpass_answer="typed-password",
    )
    _run_main(
        calls,
        {
            "FULL_NAME": "",
            "YANDEX_EMAIL": "",
            "YANDEX_APP_PASSWORD": "",
            "TO_EMAIL": "to@edu.hse.ru",
        },
    )

    assert calls.dotenv_calls == 1
    assert len(calls.input_prompts) == 2
    assert len(calls.getpass_prompts) == 1
    assert calls.report_names == ["Петров Пётр"]
    assert calls.hashed == ["report-text"]
    assert len(calls.sent) == 1
    sent = calls.sent[0]
    assert sent["from_email"] == "from@yandex.ru"
    assert sent["password"] == "typed-password"
    assert sent["to_email"] == "to@edu.hse.ru"
