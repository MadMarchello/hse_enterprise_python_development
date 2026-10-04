from homework.hashing import calculate_hashes

HELLO_MD5 = "5d41402abc4b2a76b9719d911017c592"
HELLO_SHA256 = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
EMPTY_MD5 = "d41d8cd98f00b204e9800998ecf8427e"
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
CYRILLIC_MD5 = "608333adc72f545078ede3aad71bfe74"
CYRILLIC_SHA256 = "e58f1e8c55fa105bdd3f40e5037eb0b039b5998d52c05e6cd98878dd2da5cab2"


def test_hello():
    md5_hex, sha256_hex = calculate_hashes("hello")
    assert md5_hex == HELLO_MD5
    assert sha256_hex == HELLO_SHA256


def test_empty_string():
    md5_hex, sha256_hex = calculate_hashes("")
    assert md5_hex == EMPTY_MD5
    assert sha256_hex == EMPTY_SHA256


def test_cyrillic():
    md5_hex, sha256_hex = calculate_hashes("привет")
    assert md5_hex == CYRILLIC_MD5
    assert sha256_hex == CYRILLIC_SHA256
