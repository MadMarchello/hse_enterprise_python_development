import os
from getpass import getpass

from dotenv import load_dotenv

from homework.hashing import calculate_hashes
from homework.mail import format_result_body, send_email
from homework.report import build_report


def main() -> None:
    env_loaded = load_dotenv()
    full_name = os.getenv("FULL_NAME", "").strip()
    if not env_loaded or not full_name:
        full_name = input("Введите ФИО: ").strip()

    from_email = os.getenv("YANDEX_EMAIL", "").strip()
    password = os.getenv("YANDEX_APP_PASSWORD", "").strip()
    to_email = os.getenv("TO_EMAIL", "mibelousov@edu.hse.ru").strip()
    if not from_email:
        from_email = input("Yandex email: ").strip()
    if not password:
        password = getpass("Пароль приложения: ")

    report = build_report(full_name)
    md5_hex, sha256_hex = calculate_hashes(report)
    print(report)
    print(md5_hex)
    print(sha256_hex)

    send_email(
        subject="Homework 01",
        body=format_result_body(full_name, md5_hex, sha256_hex),
        to_email=to_email,
        from_email=from_email,
        password=password,
    )


if __name__ == "__main__":
    main()
