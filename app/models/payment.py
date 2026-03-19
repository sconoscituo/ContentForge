"""
결제 모델 - 포트원(PortOne) 크레딧 충전 결제 내역 저장
충전 패키지: 10크레딧(1,000원), 50크레딧(4,500원), 100크레딧(8,000원)
"""
from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PaymentStatus:
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    FAILED = "failed"


# 크레딧 충전 패키지 정의
CREDIT_PACKAGES: dict[int, int] = {
    10: 1000,   # 10크레딧 = 1,000원
    50: 4500,   # 50크레딧 = 4,500원
    100: 8000,  # 100크레딧 = 8,000원
}


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    imp_uid: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)  # 포트원 결제 고유번호
    merchant_uid: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)  # 주문번호
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # 결제금액 (원)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)  # 충전 크레딧 수량
    status: Mapped[str] = mapped_column(String(20), default=PaymentStatus.PENDING, nullable=False)
    cancel_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Payment id={self.id} credits={self.credits} amount={self.amount} status={self.status}>"
