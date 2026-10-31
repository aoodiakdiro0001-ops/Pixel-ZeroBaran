"""
Pixel-ZeroBaran | معالج الدفعات (Batch Processor)
==================================================
يعالج مجلداً كاملاً من صور المنتجات دفعة واحدة.
يُستدعى يدوياً أو من GitHub Actions بشكل مجدول.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings, COPYRIGHT_NOTICE
from scripts.run_pipeline import PixelZeroBaranPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("pixel-zerobaran.batch")


# --------------------------------------------------------------------------- #
def batch_process(
    input_dir: Path,
    style: str = "studio_marble",
    product_description: str = "منتج فاخر",
    size: int = 1024,
    delay_between: float = 2.0,
) -> dict:
    """
    يعالج كل الصور المدعومة داخل input_dir.

    Returns:
        تقرير ملخّص: {total, ok, failed, elapsed, results[]}
    """
    pipeline = PixelZeroBaranPipeline()
    images = [
        p for p in sorted(input_dir.iterdir())
        if p.suffix.lower() in settings.supported_formats
    ]

    logger.info("تم اكتشاف %d صورة في %s", len(images), input_dir)
    if not images:
        return {"total": 0, "ok": 0, "failed": 0, "elapsed": 0, "results": []}

    t0 = time.perf_counter()
    results = []
    ok = failed = 0

    for idx, img_path in enumerate(images, 1):
        logger.info("[%d/%d] معالجة %s", idx, len(images), img_path.name)
        try:
            result = pipeline.run(
                image_bytes=img_path.read_bytes(),
                product_description=product_description,
                style=style,
                size=(size, size),
                source="batch",
                filename=img_path.name,
            )
            results.append({"file": img_path.name, "status": "ok", **result.__dict__})
            ok += 1
        except Exception as exc:  # noqa: BLE001
            logger.exception("فشل %s", img_path)
            results.append({"file": img_path.name, "status": "error", "error": str(exc)})
            failed += 1
        time.sleep(delay_between)

    elapsed = round(time.perf_counter() - t0, 2)
    logger.info("اكتملت الدفعة: ok=%d failed=%d elapsed=%.2fs", ok, failed, elapsed)
    return {
        "total": len(images),
        "ok": ok,
        "failed": failed,
        "elapsed": elapsed,
        "results": results,
    }


# --------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(description="Pixel-ZeroBaran — معالج الدفعات")
    parser.add_argument("input_dir", type=Path, help="مجلد صور المنتجات الخام")
    parser.add_argument("--style", default="studio_marble",
                        choices=list(settings.scene_presets.keys()))
    parser.add_argument("--desc", default="منتج فاخر")
    parser.add_argument("--size", type=int, default=1024)
    parser.add_argument("--delay", type=float, default=2.0,
                        help="تأخير بالثواني بين كل صورة (لتفادي حدود الـ API المجاني)")
    parser.add_argument("--report", type=Path, default=None,
                        help="مسار لحفظ تقرير JSON")
    args = parser.parse_args()

    if not args.input_dir.exists():
        print(f"❌ المجلد غير موجود: {args.input_dir}")
        sys.exit(1)

    print(f"🚀 {COPYRIGHT_NOTICE}")
    report = batch_process(
        input_dir=args.input_dir,
        style=args.style,
        product_description=args.desc,
        size=args.size,
        delay_between=args.delay,
    )

    print("\n" + "=" * 60)
    print(f"📊 ملخص الدفعة: ok={report['ok']}/{report['total']} | "
          f"failed={report['failed']} | {report['elapsed']}s")
    print("=" * 60)

    if args.report:
        import json
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        print(f"📝 تم حفظ التقرير في: {args.report}")


if __name__ == "__main__":
    main()
