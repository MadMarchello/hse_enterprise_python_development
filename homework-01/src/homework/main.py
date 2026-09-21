from dotenv import load_dotenv

from homework.hashing import calculate_hashes
from homework.report import build_report


def main() -> None:
    load_dotenv()
    report = build_report()
    md5_hex, sha256_hex = calculate_hashes(report)
    print(report)
    #print(md5_hex)
    #print(sha256_hex)


if __name__ == "__main__":
    main()
