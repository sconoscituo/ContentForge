"""
콘텐츠 라우터
콘텐츠 생성, 조회, 삭제 엔드포인트를 제공합니다.
크레딧 차감 로직이 포함되어 있습니다.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.content import Content
from app.schemas.content import (
    ContentRequest,
    ContentResponse,
    ContentListResponse,
    ContentDeleteResponse,
)
from app.services.content_generator import generate_content
from app.services.credit_manager import check_and_deduct_credits
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/v1/content", tags=["content"])


@router.post("/generate", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def generate(
    req: ContentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    콘텐츠 생성 (핵심 기능)
    1. 크레딧 잔액 확인 및 차감
    2. Gemini API로 플랫폼별 콘텐츠 생성
    3. DB에 저장 후 반환

    플랫폼별 크레딧 소모:
    - instagram: 1크레딧
    - twitter: 1크레딧
    - blog: 2크레딧
    - youtube: 3크레딧
    """
    # 크레딧 차감 (부족 시 402 에러 발생)
    credits_used = await check_and_deduct_credits(db, current_user.id, req.platform)

    try:
        # Gemini API 콘텐츠 생성
        generated_text, hashtags = await generate_content(req)
    except Exception as e:
        # 생성 실패 시 크레딧 환불 처리
        from app.services.credit_manager import add_credits
        await add_credits(db, current_user.id, credits_used)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"콘텐츠 생성에 실패했습니다. 잠시 후 다시 시도해주세요. ({str(e)})",
        )

    # 키워드를 콤마 구분 문자열로 변환
    keywords_str = ", ".join(req.keywords) if req.keywords else None

    # DB에 콘텐츠 저장
    new_content = Content(
        user_id=current_user.id,
        platform=req.platform,
        topic=req.topic,
        tone=req.tone,
        keywords=keywords_str,
        language=req.language,
        generated_text=generated_text,
        hashtags=hashtags,
        credits_used=credits_used,
    )
    db.add(new_content)
    await db.flush()
    await db.refresh(new_content)

    return new_content


@router.get("/", response_model=ContentListResponse)
async def list_contents(
    platform: str | None = Query(default=None, description="플랫폼 필터 (instagram/youtube/blog/twitter)"),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    page_size: int = Query(default=10, ge=1, le=50, description="페이지당 항목 수"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    내 콘텐츠 목록 조회
    - 페이지네이션 지원
    - 플랫폼 필터링 지원
    """
    query = select(Content).where(Content.user_id == current_user.id)

    # 플랫폼 필터 적용
    if platform:
        query = query.where(Content.platform == platform)

    # 전체 개수 조회
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar_one()

    # 페이지네이션 적용 후 최신순 정렬
    offset = (page - 1) * page_size
    query = query.order_by(Content.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    contents = result.scalars().all()

    return ContentListResponse(total=total, items=list(contents))


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    특정 콘텐츠 상세 조회
    - 본인 콘텐츠만 조회 가능
    """
    result = await db.execute(
        select(Content).where(
            Content.id == content_id,
            Content.user_id == current_user.id,
        )
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="콘텐츠를 찾을 수 없습니다.",
        )

    return content


@router.delete("/{content_id}", response_model=ContentDeleteResponse)
async def delete_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    콘텐츠 삭제
    - 본인 콘텐츠만 삭제 가능
    - 삭제 시 크레딧은 환불되지 않습니다
    """
    result = await db.execute(
        select(Content).where(
            Content.id == content_id,
            Content.user_id == current_user.id,
        )
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="콘텐츠를 찾을 수 없습니다.",
        )

    await db.delete(content)

    return ContentDeleteResponse(
        message="콘텐츠가 삭제되었습니다.",
        deleted_id=content_id,
    )
