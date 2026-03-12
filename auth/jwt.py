import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, status
from config import settings


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def verify_access_token(access_token: str) -> dict:
    try:
        payload = jwt.decode(
            access_token, settings.JWT_SECRET_KEY, algorithms=["HS256"]
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )

    return payload


http_bearer = HTTPBearer()


def verify_user(
    auth_header: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> int:
    access_token = auth_header.credentials
    payload = verify_access_token(access_token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid payload",
        )
    return user_id
