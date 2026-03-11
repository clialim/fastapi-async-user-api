import bcrypt


def hash_password(plain_password: str):
    password_hash_bytes: bytes = bcrypt.hashpw(
        plain_password.encode(),
        bcrypt.gensalt(),
    )
    return password_hash_bytes.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode(), password_hash.encode())

    except Exception:
        return False
