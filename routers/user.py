from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from database.orm import User, HealthProfile
from database.connection import get_session
from request import SignUpRequest, LoginRequest, HealthProfileCreateRequest
from auth.password import hash_password, verify_password
from auth.jwt import create_access_token, verify_user
from response import LoginResponse

router = APIRouter(tags=["User"])


@router.post(
    "/users",
    summary="유저 생성",
    description="Create a new user with email, password, and name",
    status_code=status.HTTP_201_CREATED,
)
async def signup_handler(
    body: SignUpRequest = Body(...),
    session=Depends(get_session),
):
    # [1] email 중복 검사
    stmt = select(User).where(User.email == body.email)
    user = await session.scalar(stmt)
    if user:  # ✅ 중복 시 예외 처리 추가
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )

    # [2] password 해싱
    new_user = User(
        email=body.email,
        name=body.name,
        password_hash=hash_password(password=body.password),
    )
    # [3] DB에 사용자 정보 저장
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {"message": "User created successfully"}


@router.delete(
    "/users",
    summary="유저 삭제",
    description="Delete the authenticated user and their health profile",
    status_code=status.HTTP_200_OK,
)
async def delete_user_handler(
    user_id: int = Depends(verify_user),
    session=Depends(get_session),
):
    stmt = select(User).where(User.id == user_id)
    user = await session.scalar(stmt)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await session.delete(user)
    await session.commit()


@router.post(
    "/users/login",
    summary="로그인 API",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def login_handler(
    body: LoginRequest = Body(...),  # ✅ LoginRequest로 변경
    session=Depends(get_session),
):
    # [1] email 존재 여부 확인
    stmt = select(User).where(User.email == body.email)
    user = await session.scalar(stmt)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # [2] password 검증
    verified = verify_password(
        password=body.password, hashed_password=user.password_hash
    )
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    # [3] 로그인 처리 - access_token 반환
    access_token = create_access_token(user_id=user.id)
    return LoginResponse(access_token=access_token)  # ✅ LoginResponse 객체로 반환


http_bearer = HTTPBearer(auto_error=False)


# 프로필 생성
@router.post(
    "/health-profile",
    summary="건강 프로필 생성 API",
    status_code=status.HTTP_201_CREATED,
)
async def create_health_profile_handler(
    body: HealthProfileCreateRequest = Body(...),
    session=Depends(get_session),
    user_id: int = Depends(verify_user),
):
    #  [1] HealthProfile 객체 생성
    profile_data = body.model_dump()
    new_profile = HealthProfile(user_id=user_id, **profile_data)
    #  [2] DB에 건강 프로필 저장
    session.add(new_profile)
    await session.commit()
    await session.refresh(new_profile)

    return {"message": f"Health profile created for user_id: {user_id}"}
