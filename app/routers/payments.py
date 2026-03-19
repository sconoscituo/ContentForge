"""
결제 라우터 - 포트원 크레딧 충전 결제 검증/취소/내역 조회
크레딧 패키지: 10크레딧(1,000원), 50크레딧(4,500원), 100크레딧(8,000원)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.payment import Payment, PaymentStatus, CREDIT_PACKAGES
from app.models.user import User
from app.utils.auth import get_current_active_user
from app.services.payment import verify_payment, cancel_payment

router = APIRouter(prefix="/payments", tags=["payments"])


class CreditChargeRequest(BaseModel):
    imp_uid: str
    merchant_uid: str
    credits: int  # 충전할 크레딧 수: 10, 50, 100


class PaymentCancelRequest(BaseModel):
    imp_uid: str
    reason: str = "사용자 요청 취소"


@router.post("/verify", summary="크레딧 충전 결제 검증")
async def verify_credit_charge(
    body: CreditChargeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    포트원 결제 검증 후 크레딧을 충전합니다.
    패키지: 10크레딧(1,000원), 50크레딧(4,500원), 100크레딧(8,000원)
    """
    expected_amount = CREDIT_PACKAGES.get(body.credits)
    if expected_amount is None:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 크레딧 패키지입니다. 가능한 값: {list(CREDIT_PACKAGES.keys())}",
        )

    # 중복 결제 확인
    result = await db.execute(
        select(Payment).where(Payment.imp_uid == body.imp_uid)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="이미 처리된 결제입니다.")

    # 포트원 결제 검증
    is_valid = await verify_payment(body.imp_uid, expected_amount)
    if not is_valid:
        payment = Payment(
            imp_uid=body.imp_uid,
            merchant_uid=body.merchant_uid,
            user_id=current_user.id,
            amount=expected_amount,
            credits=body.credits,
            status=PaymentStatus.FAILED,
        )
        db.add(payment)
        await db.commit()
        raise HTTPException(status_code=400, detail="결제 검증 실패: 금액이 일치하지 않습니다.")

    # 결제 내역 저장
    payment = Payment(
        imp_uid=body.imp_uid,
        merchant_uid=body.merchant_uid,
        user_id=current_user.id,
        amount=expected_amount,
        credits=body.credits,
        status=PaymentStatus.PAID,
    )
    db.add(payment)

    # 크레딧 충전
    current_user.credits_remaining += body.credits
    await db.commit()

    return {
        "message": f"{body.credits}크레딧이 충전되었습니다.",
        "credits_charged": body.credits,
        "credits_remaining": current_user.credits_remaining,
        "amount_paid": expected_amount,
    }


@router.post("/cancel", summary="결제 취소 및 크레딧 환수")
async def cancel_charge(
    body: PaymentCancelRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """결제를 취소하고 충전된 크레딧을 회수합니다."""
    result = await db.execute(
        select(Payment).where(
            Payment.imp_uid == body.imp_uid,
            Payment.user_id == current_user.id,
            Payment.status == PaymentStatus.PAID,
        )
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="취소할 결제 내역을 찾을 수 없습니다.")

    # 포트원 결제 취소
    await cancel_payment(body.imp_uid, body.reason)

    # 결제 상태 업데이트
    payment.status = PaymentStatus.CANCELLED
    payment.cancel_reason = body.reason

    # 크레딧 회수 (잔액 부족 시 0으로 처리)
    current_user.credits_remaining = max(0, current_user.credits_remaining - payment.credits)
    await db.commit()

    return {"message": "결제가 취소되고 크레딧이 회수되었습니다.", "credits_revoked": payment.credits}


@router.get("/history", summary="결제 내역 조회")
async def get_payment_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """현재 사용자의 크레딧 충전 결제 내역을 조회합니다."""
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
    )
    payments = result.scalars().all()
    return {
        "total": len(payments),
        "credits_remaining": current_user.credits_remaining,
        "payments": [
            {
                "id": p.id,
                "imp_uid": p.imp_uid,
                "merchant_uid": p.merchant_uid,
                "credits": p.credits,
                "amount": p.amount,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
            }
            for p in payments
        ],
    }
