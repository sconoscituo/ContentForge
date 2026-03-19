"""
콘텐츠 템플릿 라이브러리 라우터
"""
import json
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/templates", tags=["콘텐츠 템플릿"])

try:
    from app.config import config
    GEMINI_KEY = config.GEMINI_API_KEY
except Exception:
    GEMINI_KEY = ""

# 내장 템플릿 라이브러리
TEMPLATE_LIBRARY = {
    "sns_post": {
        "name": "SNS 포스트",
        "platforms": ["인스타그램", "트위터", "링크드인"],
        "variables": ["topic", "tone", "hashtag_count"],
    },
    "product_description": {
        "name": "상품 설명",
        "platforms": ["쇼핑몰", "네이버 스토어", "쿠팡"],
        "variables": ["product_name", "features", "target_customer"],
    },
    "blog_intro": {
        "name": "블로그 도입부",
        "platforms": ["티스토리", "네이버 블로그", "브런치"],
        "variables": ["topic", "target_keyword", "reader_persona"],
    },
    "press_release": {
        "name": "보도자료",
        "platforms": ["뉴스와이어", "PRNewswire"],
        "variables": ["company", "news_title", "key_points"],
    },
}


@router.get("/")
async def list_templates(current_user: User = Depends(get_current_user)):
    """사용 가능한 콘텐츠 템플릿 목록"""
    return {
        "templates": [
            {"id": k, **v} for k, v in TEMPLATE_LIBRARY.items()
        ],
        "total": len(TEMPLATE_LIBRARY),
    }


class TemplateGenerateRequest(BaseModel):
    template_id: str
    variables: dict
    platform: Optional[str] = None
    tone: Optional[str] = "전문적"


@router.post("/generate")
async def generate_from_template(
    request: TemplateGenerateRequest,
    current_user: User = Depends(get_current_user),
):
    """템플릿 기반 콘텐츠 생성"""
    if request.template_id not in TEMPLATE_LIBRARY:
        raise HTTPException(404, "템플릿을 찾을 수 없습니다")
    if not GEMINI_KEY:
        raise HTTPException(500, "AI 서비스 설정이 필요합니다")

    template = TEMPLATE_LIBRARY[request.template_id]
    vars_text = "\n".join([f"- {k}: {v}" for k, v in request.variables.items()])

    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        f"콘텐츠 유형: {template['name']}\n"
        f"플랫폼: {request.platform or '일반'}\n"
        f"톤: {request.tone}\n"
        f"입력 정보:\n{vars_text}\n\n"
        f"위 정보를 바탕으로 최적화된 {template['name']}을 한국어로 작성해줘."
    )
    return {
        "template_id": request.template_id,
        "template_name": template["name"],
        "platform": request.platform,
        "generated_content": response.text,
    }
