"""
사용자 라우터
회원가입, 로그인, 크레딧 조회 엔드포인트를 제공합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, CreditInfo
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.services.credit_manager import get_credits
from app.config import settings

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    회원가입
    - 이메일 중복 확인 후 계정 생성
    - 신규 사용자에게 무료 크레딧 지급
    """
    # 이메일 중복 확인
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일입니다.",
        )

    # 신규 사용자 생성
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        credits_remaining=settings.monthly_free_credits,  # 무료 크레딧 지급
        subscription_plan="free",
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    로그인
    - 이메일/비밀번호 검증 후 JWT 액세스 토큰 반환
    """
    # 사용자 조회
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다.",
        )

    access_token = create_access_token(user_id=user.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    내 계정 정보 조회
    - JWT 인증 필요
    """
    return current_user


@router.get("/credits", response_model=CreditInfo)
async def get_my_credits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    크레딧 잔액 및 구독 플랜 조회
    - JWT 인증 필요
    """
    credit_info = await get_credits(db, current_user.id)
    return CreditInfo(
        user_id=credit_info["user_id"],
        credits_remaining=credit_info["credits_remaining"],
        subscription_plan=credit_info["subscription_plan"],
    )
