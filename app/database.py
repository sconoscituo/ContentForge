"""
데이터베이스 연결 및 세션 관리
SQLAlchemy 비동기 엔진을 사용합니다.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# 비동기 SQLAlchemy 엔진 생성
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # DEBUG 모드에서 SQL 쿼리 출력
    future=True,
)

# 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """모든 ORM 모델의 기반 클래스"""
    pass


async def get_db() -> AsyncSession:
    """
    FastAPI 의존성 주입용 DB 세션 제공 함수
    요청마다 새 세션을 생성하고 요청 완료 후 닫습니다.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    애플리케이션 시작 시 테이블 생성
    모든 모델을 import한 뒤 호출해야 합니다.
    """
    # 모든 모델 import (테이블 메타데이터 등록)
    from app.models import user, content, template  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
