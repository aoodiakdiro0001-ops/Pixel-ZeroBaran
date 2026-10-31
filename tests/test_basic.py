"""
Pixel-ZeroBaran | اختبارات بسيطة للوحدات الأساسية
تنفّذ عبر: pytest tests/  أو  python -m pytest tests/
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest
from PIL import Image

# ضمان استيراد الإعدادات من جذر المشروع
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings, AUTHOR, COPYRIGHT_NOTICE


# --------------------------------------------------------------------------- #
def test_settings_loaded():
    """يتأكد أن كائن الإعدادات محمّل وله المسارات الصحيحة."""
    assert settings.project_root.exists()
    assert "studio_marble" in settings.scene_presets
    assert len(settings.scene_presets) >= 5


def test_author_info_complete():
    """يتأكد أن كل معلومات المؤلف محفوظة."""
    assert AUTHOR["name"] == "Baran Avisat"
    assert "@" in AUTHOR["email"]
    assert AUTHOR["whatsapp"].startswith("00")
    assert AUTHOR["iban"].startswith("TR")
    assert "Pixel-ZeroBaran" in COPYRIGHT_NOTICE


def test_dirs_created():
    """يتأكد أن المجلدات موجودة."""
    assert settings.raw_dir.exists()
    assert settings.output_dir.exists()
    assert settings.temp_dir.exists()


def test_make_test_image(tmp_path):
    """ينشئ صورة اختبار بسيطة (مربع أحمر)."""
    img = Image.new("RGB", (512, 512), color=(220, 30, 30))
    p = tmp_path / "test_product.png"
    img.save(p)
    assert p.exists()
    assert p.stat().st_size > 0


def test_scene_presets_have_keywords():
    """يتأكد أن كل الأنماط تحتوي على كلمات مفتاحية تجارية."""
    keywords = ["product", "studio", "commercial", "8k"]
    for key, prompt in settings.scene_presets.items():
        # كل وصف يجب أن يحوي على الأقل كلمة من القائمة
        assert any(k.lower() in prompt.lower() for k in keywords), \
            f"النمط {key} يفتقد الكلمات المفتاحية"


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # تشغيل مباشر بدون pytest
    print("تشغيل اختبارات Pixel-ZeroBaran...\n")
    tests = [
        test_settings_loaded,
        test_author_info_complete,
        test_dirs_created,
        test_scene_presets_have_keywords,
    ]
    for t in tests:
        try:
            t()
            print(f"  ✅ {t.__name__}")
        except Exception as e:
            print(f"  ❌ {t.__name__}: {e}")
    print("\nتم.")
