"""
ContentForge - FastAPI 앱 엔트리포인트
SNS 콘텐츠 자동 생성 AI SaaS

실행 방법:
    uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import content, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    앱 생명주기 관리
    - 시작 시: DB 테이블 생성
    - 종료 시: 필요한 정리 작업
    """
    # 시작 시 DB 초기화
    await init_db()
    print(f"[ContentForge] 서버 시작 - {settings.app_name} v{settings.app_version}")
    print(f"[ContentForge] DEBUG 모드: {settings.debug}")
    yield
    # 종료 시 정리 작업 (필요 시 추가)
    print("[ContentForge] 서버 종료")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "SNS 콘텐츠 자동 생성 AI SaaS. "
        "인스타그램 캡션, 유튜브 스크립트, 블로그 포스트, 트위터를 Gemini AI로 생성합니다."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 설정 (프론트엔드 연동 시 origin 수정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://contentforge.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(users.router)
app.include_router(content.router)


@app.get("/", tags=["health"])
async def root():
    """헬스체크 엔드포인트"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}
