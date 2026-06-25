"""密码哈希与验证 — 使用 hashlib (纯 Python, 无 C 依赖)"""

import hashlib
import os


def hash_password(password: str) -> str:
    """PBKDF2-SHA256 哈希，返回格式：algorithm$salt$hash"""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600_000)
    return f"pbkdf2_sha256${salt.hex()}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        algorithm, salt_hex, key_hex = hashed_password.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 600_000)
        return new_key == expected_key
    except (ValueError, AttributeError):
        return False
