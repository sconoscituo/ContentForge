"""
크레딧 관리 서비스
사용자 크레딧 차감, 충전, 조회 로직을 담당합니다.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.config import settings


# 플랫폼별 크레딧 소모량 매핑
PLATFORM_CREDIT_COST: dict[str, int] = {
    "instagram": settings.credits_instagram,  # 1크레딧
    "youtube": settings.credits_youtube,      # 3크레딧
    "blog": settings.credits_blog,            # 2크레딧
    "twitter": settings.credits_twitter,      # 1크레딧
}


async def get_credit_cost(platform: str) -> int:
    """플랫폼에 따른 크레딧 소모량 반환"""
    return PLATFORM_CREDIT_COST.get(platform, 1)


async def check_and_deduct_credits(
    db: AsyncSession,
    user_id: int,
    platform: str,
) -> int:
    """
    크레딧 확인 후 차감
    - 크레딧 부족 시 402 에러 발생
    - 차감 성공 시 소모된 크레딧 수 반환
    """
    # 사용자 조회
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    cost = await get_credit_cost(platform)

    # 크레딧 잔액 확인
    if user.credits_remaining < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"크레딧이 부족합니다. "
                f"필요: {cost}크레딧, 잔액: {user.credits_remaining}크레딧. "
                "플랜을 업그레이드하거나 크레딧을 충전하세요."
            ),
        )

    # 크레딧 차감
    user.credits_remaining -= cost
    await db.flush()  # 즉시 DB에 반영 (commit은 미루기)

    return cost


async def add_credits(
    db: AsyncSession,
    user_id: int,
    amount: int,
) -> int:
    """
    크레딧 충전
    - amount 만큼 크레딧을 추가합니다.
    - 충전 후 잔액을 반환합니다.
    """
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="충전 크레딧은 1 이상이어야 합니다.",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    user.credits_remaining += amount
    await db.flush()

    return user.credits_remaining


async def get_credits(db: AsyncSession, user_id: int) -> dict:
    """
    크레딧 잔액 및 구독 플랜 조회
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    return {
        "user_id": user.id,
        "credits_remaining": user.credits_remaining,
        "subscription_plan": user.subscription_plan,
        "platform_costs": PLATFORM_CREDIT_COST,
    }
