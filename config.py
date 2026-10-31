"""
Pixel-ZeroBaran | الإعدادات المركزية للمشروع
================================================
المؤلف: Baran Avisat
البريد: Baranavisat@gmail.com
الوتس: 00905313263722

يقوم هذا الملف بتحميل كل المتغيرات البيئية من ملف .env
ويوّلد كائن إعدادات موحد لكل طبقات النظام.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# تحميل ملف .env إن وُجد
PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")


# --------------------------------------------------------------------------- #
#  معلومات المُؤلِّف وحقوق الملكية الفكرية                                      #
# --------------------------------------------------------------------------- #
AUTHOR = {
    "name": "Baran Avisat",
    "email": "Baranavisat@gmail.com",
    "whatsapp": "00905313263722",
    "iban": "TR10 0001 0090 1008 4013 0050 01",
    "project": "Pixel-ZeroBaran",
    "version": "1.0.0",
    "license": "Proprietary - All Rights Reserved (Free to Use)",
}

COPYRIGHT_NOTICE = (
    f"© {AUTHOR['name']} — Project '{AUTHOR['project']}' v{AUTHOR['version']}. "
    "All rights reserved. Built using 100% free and open-source resources."
)


# --------------------------------------------------------------------------- #
#  إعدادات الأنظمة الخارجية                                                   #
# --------------------------------------------------------------------------- #
@dataclass
class Settings:
    """كائن إعدادات مركزي يحقن في كل الوحدات."""

    # ---------- Hugging Face ----------
    hf_token: str = field(default_factory=lambda: os.getenv("HF_TOKEN", ""))
    hf_model_bg: str = field(
        default_factory=lambda: os.getenv(
            "HF_MODEL_BG", "stabilityai/stable-diffusion-xl-base-1.0"
        )
    )
    hf_model_inpaint: str = field(
        default_factory=lambda: os.getenv(
            "HF_MODEL_INPAINT", "runwayml/stable-diffusion-inpainting"
        )
    )

    # ---------- Google Gemini ----------
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    )

    # ---------- Supabase ----------
    supabase_url: str = field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    supabase_key: str = field(default_factory=lambda: os.getenv("SUPABASE_KEY", ""))
    supabase_bucket_raw: str = field(
        default_factory=lambda: os.getenv("SUPABASE_BUCKET_RAW", "pixel-raw")
    )
    supabase_bucket_generated: str = field(
        default_factory=lambda: os.getenv("SUPABASE_BUCKET_GENERATED", "pixel-generated")
    )

    # ---------- Telegram ----------
    telegram_bot_token: str = field(
        default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", "")
    )
    telegram_chat_id: str = field(
        default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", "")
    )

    # ---------- مسارات محلية ----------
    project_root: Path = field(default_factory=lambda: PROJECT_ROOT)
    raw_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "assets" / "raw")
    output_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "assets" / "output")
    temp_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "assets" / "temp")

    # ---------- إعدادات المعالجة ----------
    default_output_size: tuple = (1024, 1024)
    jpeg_quality: int = 92
    max_batch_size: int = 25
    supported_formats: List[str] = field(
        default_factory=lambda: [".jpg", ".jpeg", ".png", ".webp", ".bmp"]
    )

    # ---------- سيناريوهات الخلفية المُعدّة مسبقاً ----------
    scene_presets: dict = field(
        default_factory=lambda: {
            "studio_marble": (
                "professional product photography, luxury marble surface, "
                "soft studio lighting, bokeh background, high-end commercial, "
                "8k, ultra detailed, sharp focus"
            ),
            "sunny_beach": (
                "product placed on sunny tropical beach, golden hour, "
                "soft sand, ocean waves background, bright natural light, "
                "commercial advertising style, 8k"
            ),
            "minimal_white": (
                "minimalist pure white background, soft shadow, "
                "centered product, commercial e-commerce style, "
                "clean aesthetic, 8k studio shot"
            ),
            "luxury_dark": (
                "luxury dark moody studio, dramatic rim lighting, "
                "premium product placement, cinematic atmosphere, "
                "8k advertising photography"
            ),
            "forest_nature": (
                "product in lush green forest setting, dappled sunlight, "
                "natural moss and wood surface, organic commercial vibe, 8k"
            ),
        }
    )

    def ensure_dirs(self) -> None:
        """ينشئ كل المجلدات المحلية الضرورية إن لم تكن موجودة."""
        for d in (self.raw_dir, self.output_dir, self.temp_dir):
            d.mkdir(parents=True, exist_ok=True)

    def validate(self) -> List[str]:
        """يرجع قائمة بالأخطاء (المفاتيح الناقصة الحرجة)."""
        errors: List[str] = []
        if not self.hf_token and not self.gemini_api_key:
            errors.append(
                "يجب توفير إما HF_TOKEN أو GEMINI_API_KEY على الأقل لتشغيل الطبقة التوليدية."
            )
        if not self.supabase_url or not self.supabase_key:
            errors.append("إعدادات Supabase ناقصة — التخزين السحابي سيكون معطلاً.")
        if not self.telegram_bot_token:
            errors.append("TELEGRAM_BOT_TOKEN ناقص — بوت التسليم معطّل.")
        return errors


# كائن إعدادات وحيد للإستيراد في أي مكان
settings = Settings()
settings.ensure_dirs()


__all__ = ["Settings", "settings", "AUTHOR", "COPYRIGHT_NOTICE"]
