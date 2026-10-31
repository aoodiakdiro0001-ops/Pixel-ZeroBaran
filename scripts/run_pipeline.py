"""
Pixel-ZeroBaran | خط الأنابيب الكامل (End-to-End Pipeline)
============================================================
سكريبت موحّد يربط كل الطبقات الأربع: رفع → عزل → توليد → تخزين → تسليم.
يُستخدم من البوت، من لوحة Streamlit، أو من سكريبت الدفعات.
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings, AUTHOR, COPYRIGHT_NOTICE
from core.background_remover import BackgroundRemover
from core.ai_generator import AIVisualEngine
from core.storage import get_storage

logger = logging.getLogger("pixel-zerobaran.pipeline")


# --------------------------------------------------------------------------- #
@dataclass
class PipelineResult:
    """نتيجة موحّدة لكل تشغيل للـ pipeline."""
    cutout_path: str
    generated_path: str
    scene_prompt: str
    ad_caption: str
    ad_hashtags: list
    elapsed_seconds: float
    style: str
    status: str = "ok"
    error: Optional[str] = None


# --------------------------------------------------------------------------- #
class PixelZeroBaranPipeline:
    """خط الأنابيب الكامل لمعالجة صورة منتج واحدة."""

    def __init__(self):
        logger.info("تهيئة مكونات Pipeline...")
        self.remover = BackgroundRemover()
        self.engine = AIVisualEngine()
        self.storage = get_storage()
        logger.info("Pipeline جاهز.")

    # ------------------------------------------------------------------ #
    def run(
        self,
        image_bytes: bytes,
        product_description: str = "منتج فاخر",
        style: str = "studio_marble",
        size: Optional[tuple[int, int]] = None,
        source: str = "pipeline",
        filename: str = "product.png",
    ) -> PipelineResult:
        """
        ينفّذ كامل الـ pipeline على صورة واحدة.

        Args:
            image_bytes: بيانات صورة المنتج الخام.
            product_description: وصف المنتج للذكاء الاصطناعي.
            style: مفتاح النمط من settings.scene_presets.
            size: أبعاد الإخراج (None = الافتراضي 1024×1024).
            source: مصدر الطلب (للسجل).
            filename: اسم الملف للرفع.

        Returns:
            PipelineResult — كل المعلومات الجاهزة.
        """
        size = size or settings.default_output_size
        if style not in settings.scene_presets:
            raise ValueError(f"نمط غير معروف: {style}")

        # 1) رفع الصورة الخام
        raw_url = self.storage.upload_raw(image_bytes, filename)

        # 2) إزالة الخلفية
        cutout_bytes, _ = self.remover.remove_background(image_bytes=image_bytes)

        # 3) توليد الإعلان
        result = self.engine.generate_ad(
            product_png_bytes=cutout_bytes,
            product_description=product_description,
            style=style,
            size=size,
        )

        # 4) حفظ الناتج
        out_filename = f"{Path(filename).stem}_ad.jpg"
        generated_url = self.storage.upload_generated(result["image_bytes"], out_filename)

        # 5) تسجيل السجل
        self.storage.log_asset(
            source=source,
            raw_path=raw_url,
            generated_path=generated_url,
            scene_prompt=result["scene_prompt"],
            style=style,
            ad_caption=result["ad_copy"].get("caption", ""),
            ad_hashtags=result["ad_copy"].get("hashtags", []),
            elapsed_seconds=result["meta"]["elapsed_seconds"],
            status="ok",
        )

        return PipelineResult(
            cutout_path=raw_url,
            generated_path=generated_url,
            scene_prompt=result["scene_prompt"],
            ad_caption=result["ad_copy"].get("caption", ""),
            ad_hashtags=result["ad_copy"].get("hashtags", []),
            elapsed_seconds=result["meta"]["elapsed_seconds"],
            style=style,
            status="ok",
        )


# --------------------------------------------------------------------------- #
def main():
    """تشغيل سريع من CLI: python scripts/run_pipeline.py <image_path> [style] [desc]"""
    import argparse
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    parser = argparse.ArgumentParser(description="Pixel-ZeroBaran — تشغيل خط الأنابيب")
    parser.add_argument("image", type=Path, help="مسار صورة المنتج الخام")
    parser.add_argument("--style", default="studio_marble",
                        choices=list(settings.scene_presets.keys()))
    parser.add_argument("--desc", default="منتج فاخر")
    parser.add_argument("--size", type=int, default=1024)
    args = parser.parse_args()

    if not args.image.exists():
        print(f"❌ الملف غير موجود: {args.image}")
        sys.exit(1)

    print(f"🚀 {COPYRIGHT_NOTICE}")
    pipeline = PixelZeroBaranPipeline()
    result = pipeline.run(
        image_bytes=args.image.read_bytes(),
        product_description=args.desc,
        style=args.style,
        size=(args.size, args.size),
        source="cli",
        filename=args.image.name,
    )

    print("\n" + "=" * 60)
    print("✅ اكتمل خط الأنابيب بنجاح!")
    print("=" * 60)
    print(f"🖼️ صورة الإعلان: {result.generated_path}")
    print(f"⏱️ استغرق: {result.elapsed_seconds}s")
    print(f"🎨 النمط: {result.style}")
    print(f"📝 النص: {result.ad_caption}")
    if result.ad_hashtags:
        print(" ".join(result.ad_hashtags))
    print(f"🧠 وصف المشهد: {result.scene_prompt}")


if __name__ == "__main__":
    main()
