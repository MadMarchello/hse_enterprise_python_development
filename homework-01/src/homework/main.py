import os

from dotenv import load_dotenv

from homework.hashing import calculate_hashes
from homework.report import build_report


def main() -> None:
    env_loaded = load_dotenv()
    full_name = os.getenv("FULL_NAME", "").strip()
    if not env_loaded or not full_name:
        full_name = input("Введите ФИО: ").strip()
    report = build_report(full_name)
    md5_hex, sha256_hex = calculate_hashes(report)
    print(report)
    print(md5_hex)
    print(sha256_hex)


if __name__ == "__main__":
    main()
