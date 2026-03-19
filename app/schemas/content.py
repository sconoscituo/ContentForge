"""
콘텐츠 관련 Pydantic 스키마
콘텐츠 생성 요청 및 응답 데이터 검증에 사용됩니다.
"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


# 지원 플랫폼 타입
Platform = Literal["instagram", "youtube", "blog", "twitter"]

# 지원 톤 타입
Tone = Literal["casual", "professional", "humorous", "inspirational", "educational"]

# 지원 언어
Language = Literal["ko", "en"]


class ContentRequest(BaseModel):
    """콘텐츠 생성 요청 스키마"""
    platform: Platform = Field(..., description="콘텐츠 생성 플랫폼")
    topic: str = Field(..., min_length=2, max_length=500, description="콘텐츠 주제")
    tone: Tone = Field(default="casual", description="콘텐츠 톤/스타일")
    keywords: list[str] = Field(
        default=[], max_length=10, description="포함할 키워드 목록 (최대 10개)"
    )
    language: Language = Field(default="ko", description="출력 언어 (ko/en)")


class ContentResponse(BaseModel):
    """콘텐츠 생성 응답 스키마"""
    id: int
    platform: str
    topic: str
    tone: str
    keywords: str | None
    language: str
    generated_text: str
    hashtags: str | None
    credits_used: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentListResponse(BaseModel):
    """콘텐츠 목록 응답 스키마"""
    total: int
    items: list[ContentResponse]


class ContentDeleteResponse(BaseModel):
    """콘텐츠 삭제 응답 스키마"""
    message: str
    deleted_id: int
