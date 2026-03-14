import bcrypt


def hash_password(password: str) -> bytes:
    password_hash_bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    return password_hash_bytes.decode()


def verify_password(password: str, hashed_password: bytes) -> bool:
    # plain_password : 사용자가 입력한 비밀번호
    # hashed_password : DB에 저장된 해시된 비밀번호

    try:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
    except ValueError:
        return False
