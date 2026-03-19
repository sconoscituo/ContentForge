"""ContentForge 구독 플랜"""
from enum import Enum

class PlanType(str, Enum):
    FREE = "free"
    CREATOR = "creator"  # 월 14,900원
    AGENCY = "agency"    # 월 49,900원

PLAN_LIMITS = {
    PlanType.FREE:    {"content_per_month": 5,   "platforms": ["blog"],                       "ai_image_prompt": False, "seo_optimize": False},
    PlanType.CREATOR: {"content_per_month": 50,  "platforms": ["blog","instagram","youtube"],  "ai_image_prompt": True,  "seo_optimize": True},
    PlanType.AGENCY:  {"content_per_month": 500, "platforms": ["blog","instagram","youtube","twitter","linkedin"], "ai_image_prompt": True, "seo_optimize": True},
}

PLAN_PRICES_KRW = {PlanType.FREE: 0, PlanType.CREATOR: 14900, PlanType.AGENCY: 49900}
