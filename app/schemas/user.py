"""
사용자 관련 Pydantic 스키마
요청/응답 데이터 검증 및 직렬화에 사용됩니다.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """회원가입 요청 스키마"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="최소 8자 이상의 비밀번호")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """비밀번호 강도 검증"""
        if not any(c.isdigit() for c in v):
            raise ValueError("비밀번호에 숫자가 최소 1개 포함되어야 합니다.")
        return v


class UserLogin(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""
    id: int
    email: str
    credits_remaining: int
    subscription_plan: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT 토큰 응답 스키마"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT 페이로드 스키마"""
    user_id: int | None = None


class CreditInfo(BaseModel):
    """크레딧 잔액 응답 스키마"""
    user_id: int
    credits_remaining: int
    subscription_plan: str
