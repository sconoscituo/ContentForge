"""
콘텐츠 모델
AI가 생성한 SNS 콘텐츠를 저장합니다.
플랫폼: instagram / youtube / blog / twitter
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Content(Base):
    __tablename__ = "contents"

    # 기본 키
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 소유자 (외래 키)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 생성 요청 파라미터
    platform: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # instagram / youtube / blog / twitter
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    tone: Mapped[str] = mapped_column(
        String(100), nullable=False, default="casual"
    )  # casual / professional / humorous / inspirational
    keywords: Mapped[str] = mapped_column(
        String(500), nullable=True
    )  # 콤마 구분 키워드
    language: Mapped[str] = mapped_column(
        String(10), nullable=False, default="ko"
    )  # ko / en

    # AI 생성 결과
    generated_text: Mapped[str] = mapped_column(Text, nullable=False)
    hashtags: Mapped[str] = mapped_column(
        Text, nullable=True
    )  # 콤마 구분 해시태그 또는 JSON 문자열
    credits_used: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # 관계 - 소유 사용자
    user: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="contents"
    )

    def __repr__(self) -> str:
        return f"<Content id={self.id} platform={self.platform} user_id={self.user_id}>"
