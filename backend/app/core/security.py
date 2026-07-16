"""密码哈希与验证 + SMTP 密码加解密"""

import base64
import hashlib
import os

from cryptography.fernet import Fernet

from app.config import settings


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


# ── SMTP 密码加解密（Fernet） ──

_ENCRYPTION_PREFIX = "enc:"


def _get_fernet() -> Fernet:
    """从 SECRET_KEY 派生 Fernet 密钥（SHA256 → base64 32 字节）"""
    key_bytes = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


def encrypt_smtp_password(plaintext: str) -> str:
    """加密 SMTP 密码，返回 enc:<ciphertext> 格式"""
    if not plaintext:
        return plaintext
    if plaintext.startswith(_ENCRYPTION_PREFIX):
        return plaintext  # 已经加密
    ciphertext = _get_fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")
    return _ENCRYPTION_PREFIX + ciphertext


def decrypt_smtp_password(maybe_encrypted: str) -> str:
    """解密 SMTP 密码；如果不是 enc: 前缀则原样返回（兼容旧数据）"""
    if not maybe_encrypted:
        return maybe_encrypted
    if not maybe_encrypted.startswith(_ENCRYPTION_PREFIX):
        return maybe_encrypted  # 明文旧数据，兼容
    ciphertext = maybe_encrypted[len(_ENCRYPTION_PREFIX):]
    try:
        return _get_fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except Exception:
        return maybe_encrypted  # 解密失败，返回原值
