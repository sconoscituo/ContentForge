"""
콘텐츠 생성 서비스
Gemini API를 사용하여 플랫폼별 SNS 콘텐츠를 생성합니다.

플랫폼별 출력:
- instagram: 캡션 + 해시태그
- youtube: 스크립트 + 썸네일 설명
- blog: 제목 + 본문 + SEO 태그
- twitter: 트윗 본문 (280자 이내)
"""

import json
import google.generativeai as genai

from app.config import settings
from app.schemas.content import ContentRequest

# Gemini API 초기화
genai.configure(api_key=settings.gemini_api_key)


def _build_prompt(req: ContentRequest) -> str:
    """
    플랫폼에 맞는 Gemini 프롬프트를 생성합니다.
    출력은 항상 JSON 형식으로 요청합니다.
    """
    language_label = "한국어" if req.language == "ko" else "English"
    keywords_str = ", ".join(req.keywords) if req.keywords else "없음"

    tone_map = {
        "casual": "친근하고 편안한",
        "professional": "전문적이고 신뢰감 있는",
        "humorous": "유머러스하고 재치 있는",
        "inspirational": "영감을 주고 동기부여가 되는",
        "educational": "교육적이고 정보 전달 중심의",
    }
    tone_label = tone_map.get(req.tone, "친근하고 편안한")

    if req.platform == "instagram":
        return f"""
당신은 인스타그램 마케팅 전문가입니다.
아래 조건으로 인스타그램 게시물을 작성해주세요.

- 주제: {req.topic}
- 톤: {tone_label}
- 포함 키워드: {keywords_str}
- 언어: {language_label}

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
  "caption": "인스타그램 캡션 (이모지 포함, 5-10문장)",
  "hashtags": ["해시태그1", "해시태그2", "해시태그3", "해시태그4", "해시태그5"]
}}
"""

    elif req.platform == "youtube":
        return f"""
당신은 유튜브 크리에이터 전문가입니다.
아래 조건으로 유튜브 영상 스크립트와 썸네일 설명을 작성해주세요.

- 주제: {req.topic}
- 톤: {tone_label}
- 포함 키워드: {keywords_str}
- 언어: {language_label}

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
  "title": "유튜브 영상 제목 (클릭을 유도하는 제목)",
  "script": "영상 스크립트 (인트로-본문-아웃트로 구조, 최소 300자)",
  "thumbnail_description": "썸네일 이미지 설명 (시각적 요소 포함)",
  "tags": ["태그1", "태그2", "태그3", "태그4", "태그5"]
}}
"""

    elif req.platform == "blog":
        return f"""
당신은 SEO 최적화 블로그 작가입니다.
아래 조건으로 블로그 포스트를 작성해주세요.

- 주제: {req.topic}
- 톤: {tone_label}
- 포함 키워드: {keywords_str}
- 언어: {language_label}

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
  "title": "SEO 최적화된 블로그 제목",
  "content": "블로그 본문 (서론-본론-결론 구조, 마크다운 형식, 최소 500자)",
  "meta_description": "검색 엔진용 메타 설명 (150자 이내)",
  "seo_tags": ["SEO태그1", "SEO태그2", "SEO태그3", "SEO태그4", "SEO태그5"]
}}
"""

    elif req.platform == "twitter":
        return f"""
당신은 트위터/X 마케팅 전문가입니다.
아래 조건으로 트윗을 작성해주세요.

- 주제: {req.topic}
- 톤: {tone_label}
- 포함 키워드: {keywords_str}
- 언어: {language_label}

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
  "tweet": "트윗 본문 (280자 이내, 임팩트 있게)",
  "hashtags": ["해시태그1", "해시태그2", "해시태그3"]
}}
"""

    else:
        raise ValueError(f"지원하지 않는 플랫폼입니다: {req.platform}")


def _parse_response(platform: str, raw: str) -> dict:
    """
    Gemini 응답 JSON을 파싱합니다.
    JSON 파싱 실패 시 원본 텍스트를 반환합니다.
    """
    # 마크다운 코드블록 제거 (```json ... ``` 형태)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 플랫폼 기본 구조로 래핑
        return {"raw_content": raw, "parse_error": True}


def _format_result(platform: str, parsed: dict) -> tuple[str, str]:
    """
    파싱된 결과를 (generated_text, hashtags) 튜플로 변환합니다.
    """
    if parsed.get("parse_error"):
        return parsed.get("raw_content", ""), ""

    if platform == "instagram":
        caption = parsed.get("caption", "")
        tags = parsed.get("hashtags", [])
        return caption, " ".join(f"#{t.lstrip('#')}" for t in tags)

    elif platform == "youtube":
        title = parsed.get("title", "")
        script = parsed.get("script", "")
        thumb = parsed.get("thumbnail_description", "")
        tags = parsed.get("tags", [])
        body = f"[제목]\n{title}\n\n[스크립트]\n{script}\n\n[썸네일 설명]\n{thumb}"
        return body, " ".join(f"#{t.lstrip('#')}" for t in tags)

    elif platform == "blog":
        title = parsed.get("title", "")
        content = parsed.get("content", "")
        meta = parsed.get("meta_description", "")
        tags = parsed.get("seo_tags", [])
        body = f"# {title}\n\n{content}\n\n---\n**메타 설명:** {meta}"
        return body, ", ".join(tags)

    elif platform == "twitter":
        tweet = parsed.get("tweet", "")
        tags = parsed.get("hashtags", [])
        return tweet, " ".join(f"#{t.lstrip('#')}" for t in tags)

    return str(parsed), ""


async def generate_content(req: ContentRequest) -> tuple[str, str]:
    """
    Gemini API를 호출하여 플랫폼별 콘텐츠를 생성합니다.

    Returns:
        (generated_text, hashtags) 튜플
    """
    model = genai.GenerativeModel("gemini-pro")
    prompt = _build_prompt(req)

    # Gemini API 호출 (동기 SDK를 사용하므로 직접 호출)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.8,        # 창의성 조절
            max_output_tokens=2048, # 최대 출력 토큰
        ),
    )

    raw_text = response.text
    parsed = _parse_response(req.platform, raw_text)
    generated_text, hashtags = _format_result(req.platform, parsed)

    return generated_text, hashtags
