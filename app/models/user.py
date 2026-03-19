"""
사용자 모델
이메일/비밀번호 기반 인증, 크레딧 잔액, 구독 플랜을 관리합니다.
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    # 기본 키
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 인증 정보
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # 크레딧 및 구독
    credits_remaining: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    subscription_plan: Mapped[str] = mapped_column(
        String(50), default="free", nullable=False
    )  # free / basic / pro

    # 상태
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 타임스탬프
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

    # 관계 - 생성한 콘텐츠 목록
    contents: Mapped[list["Content"]] = relationship(  # noqa: F821
        "Content", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} plan={self.subscription_plan}>"
