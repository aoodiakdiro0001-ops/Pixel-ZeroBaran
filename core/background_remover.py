"""
Pixel-ZeroBaran | الطبقة الأولى: المعالجة وإزالة الخلفية
==========================================================
تستخدم مكتبة Rembg مفتوحة المصدر لعزل المنتجات بدقة عالية.
"""

from __future__ import annotations

import io
import logging
import time
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image

logger = logging.getLogger("pixel-zerobaran.bg")

# استيراد متأخر لـ rembg حتى لا يفشل الاستيراد إن لم تُثبّت بعد
def _import_rembg():
    try:
        from rembg import remove, new_session  # type: ignore
        return remove, new_session
    except ImportError as exc:
        raise ImportError(
            "مكتبة rembg غير مثبتة. ثبّتها عبر: pip install rembg[gpu]  (أو rembg بدون GPU)"
        ) from exc


class BackgroundRemover:
    """مسؤول عن عزل المنتج عن خلفيته الأصلية."""

    def __init__(self, model_name: str = "u2net"):
        self._remove, self._new_session = _import_rembg()
        self.model_name = model_name
        # تجهيز جلسة المعالجة مرة واحدة لتحسين الأداء
        logger.info("تهيئة جلسة Rembg بالنموذج: %s", model_name)
        self._session = self._new_session(model_name)
        logger.info("جاهز — BackgroundRemover يعمل الآن.")

    # ------------------------------------------------------------------ #
    def remove_background(
        self,
        image_bytes: bytes | None = None,
        image_path: Path | str | None = None,
        alpha_matting: bool = False,
        sharpen: bool = True,
    ) -> Tuple[bytes, dict]:
        """
        يزيل الخلفية من صورة.

        Args:
            image_bytes: بيانات الصورة الخام (يُفضّل إن وُجدت).
            image_path: مسار الصورة البديل.
            alpha_matting: تفعيل تنعيم الحواف (أبطأ لكن أدق).
            sharpen: تطبيق شحذ بسيط على الحواف.

        Returns:
            (png_bytes, meta) — بيانات PNG بشفافية + معلومات الأداء.
        """
        if image_bytes is None and image_path is None:
            raise ValueError("يجب تمرير إما image_bytes أو image_path.")

        if image_bytes is None:
            image_bytes = Path(image_path).read_bytes()  # type: ignore

        t0 = time.perf_counter()
        logger.info("بدء إزالة الخلفية — حجم الصورة: %.1f KB", len(image_bytes) / 1024)

        result_bytes = self._remove(
            image_bytes,
            session=self._session,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=8,
        )

        if sharpen:
            img = Image.open(io.BytesIO(result_bytes)).convert("RGBA")
            img = self._sharpen_alpha(img)
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            result_bytes = buf.getvalue()

        elapsed = time.perf_counter() - t0
        meta = {
            "elapsed_seconds": round(elapsed, 3),
            "model": self.model_name,
            "alpha_matting": alpha_matting,
            "output_format": "PNG",
            "output_bytes": len(result_bytes),
        }
        logger.info("اكتمل العزل خلال %.3fs — الناتج %.1f KB",
                    elapsed, len(result_bytes) / 1024)
        return result_bytes, meta

    # ------------------------------------------------------------------ #
    @staticmethod
    def _sharpen_alpha(img: Image.Image) -> Image.Image:
        """شحذ بسيط لقناة الألفا لتحسين حواف المنتج المعزول."""
        from PIL import ImageFilter
        alpha = img.split()[-1]
        alpha = alpha.filter(ImageFilter.SMOOTH_MORE)
        alpha = alpha.point(lambda p: 255 if p > 25 else 0)
        img.putalpha(alpha)
        return img

    # ------------------------------------------------------------------ #
    def process_directory(
        self, input_dir: Path | str, output_dir: Path | str
    ) -> list[dict]:
        """
        يعالج كل الصور داخل مجلد دفعة واحدة.

        Returns:
            قائمة نتائج لكل صورة.
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results: list[dict] = []
        for img_path in sorted(input_dir.iterdir()):
            if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
                continue
            try:
                png_bytes, meta = self.remove_background(image_path=img_path)
                out_path = output_dir / f"{img_path.stem}_cutout.png"
                out_path.write_bytes(png_bytes)
                meta.update({"input": str(img_path), "output": str(out_path), "status": "ok"})
            except Exception as exc:  # noqa: BLE001
                meta = {"input": str(img_path), "status": "error", "error": str(exc)}
                logger.exception("فشل معالجة %s", img_path)
            results.append(meta)
        return results


__all__ = ["BackgroundRemover"]
