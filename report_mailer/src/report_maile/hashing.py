import hashlib


def calculate_hashes(text: str) -> tuple[str, str]:
    data = text.encode("utf-8")
    return hashlib.md5(data).hexdigest(), hashlib.sha256(data).hexdigest()
