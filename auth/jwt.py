from operator import sub

import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status

from config import settings


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def verify_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.DecodeError:
        raise ValueError("Invalid token")
    return payload["sub"]


http_bearer = HTTPBearer()


def verify_user(
    auth_header: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> int:
    access_token = auth_header.credentials
    user_id = verify_access_token(access_token)  # ✅ 반환값이 바로 user_id
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    return int(user_id)
