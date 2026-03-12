from fastapi import Depends, Body, HTTPException, status, APIRouter
from sqlalchemy import select
from auth.password import hash_password, verify_password
from auth.jwt import create_access_token, verify_user
from database.connection import get_session
from database.orm import User, HealthProfile
from request import SignUpRequest, LoginRequest, HealthProfileCreateRequest
from response import UserResponse, LoginResponse, HealthProfileResponse

router = APIRouter(tags=["User"])


@router.post(
    "/users",
    summary="회원가입 API",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def signup_handler(
    body: SignUpRequest = Body(...),
    session=Depends(get_session),
):
    stmt = select(User).where(User.email == body.email)
    user = await session.scalar(stmt)

    if user:
        raise HTTPException(status_code=409, detail="email already exists")

    new_user = User(
        email=body.email,
        password_hash=hash_password(plain_password=body.password),
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.post(
    "/users/login",
    summary="로그인 API",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def login_handler(
    body: LoginRequest = Body(...),
    session=Depends(get_session),
):

    stmt = select(User).where(User.email == body.email)
    user: User | None = await session.scalar(stmt)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized",
        )

    verified = verify_password(
        plain_password=body.password, password_hash=user.password_hash
    )
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized"
        )
    access_token = create_access_token(user_id=user.id)
    return {"access_token": access_token}


@router.post(
    "/health-profiles",
    summary="건강 프로필 생성 API",
    status_code=status.HTTP_201_CREATED,
    response_model=HealthProfileResponse,
)
async def create_health_profile_handler(
    user_id: int = Depends(verify_user),
    body: HealthProfileCreateRequest = Body(...),
    session=Depends(get_session),
):

    stmt = select(HealthProfile).where(HealthProfile.user_id == user_id)
    existing = await session.scalar(stmt)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="health profile already exists",
        )
    profile_data = body.model_dump()
    new_profile = HealthProfile(user_id=user_id, **profile_data)

    session.add(new_profile)
    await session.commit()
    await session.refresh(new_profile)
    return new_profile
