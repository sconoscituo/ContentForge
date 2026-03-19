"""
콘텐츠 템플릿 모델
플랫폼별 프롬프트 템플릿을 저장합니다.
공개 템플릿은 모든 사용자가 사용할 수 있습니다.
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ContentTemplate(Base):
    __tablename__ = "content_templates"

    # 기본 키
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 템플릿 정보
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    platform: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # instagram / youtube / blog / twitter

    # 프롬프트 템플릿 (Jinja2 스타일 변수 지원)
    # 예: "{{topic}}에 대한 {{tone}} 톤의 인스타그램 캡션을 작성해주세요."
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)

    # 공개 여부 (True면 모든 사용자 사용 가능)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 설명
    description: Mapped[str] = mapped_column(String(500), nullable=True)

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

    def __repr__(self) -> str:
        return f"<ContentTemplate id={self.id} name={self.name} platform={self.platform}>"
