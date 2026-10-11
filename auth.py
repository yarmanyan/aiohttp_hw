"""Модуль хеширования паролей."""

import bcrypt


def hash_password(password: str) -> str:
    """Хеширует пароль с помощью bcrypt.

    :param password: пароль в открытом виде;
    :return: хеш пароля в виде строки.
    """
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")