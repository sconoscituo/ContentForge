"""
애플리케이션 설정 관리
환경변수에서 설정값을 로드하고 전역으로 제공합니다.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Gemini API
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")

    # 데이터베이스
    database_url: str = Field(
        default="sqlite+aiosqlite:///./contentforge.db",
        env="DATABASE_URL",
    )

    # JWT 인증
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24시간

    # 앱 설정
    debug: bool = Field(default=False, env="DEBUG")
    app_name: str = "ContentForge"
    app_version: str = "0.1.0"

    # 크레딧 정책
    monthly_free_credits: int = Field(default=10, env="MONTHLY_FREE_CREDITS")

    # 플랫폼별 크레딧 소모량
    credits_instagram: int = 1
    credits_youtube: int = 3
    credits_blog: int = 2
    credits_twitter: int = 1

    # 포트원(PortOne) 결제 연동
    portone_api_key: str = Field(default="", env="PORTONE_API_KEY")
    portone_api_secret: str = Field(default="", env="PORTONE_API_SECRET")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 싱글톤 설정 인스턴스
settings = Settings()
