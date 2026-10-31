"""
Pixel-ZeroBaran | نقطة الدخول الموحّدة
======================================
سكريبت واحد لإطلاق أي مكون من المشروع:
  python main.py bot        → تشغيل بوت تليجرام
  python main.py dashboard  → تشغيل لوحة Streamlit
  python main.py pipeline   → تشغيل خط الأنابيب على صورة واحدة
  python main.py batch      → معالجة دفعة كاملة
  python main.py info       → عرض معلومات المؤلف وحقوق الملكية
  python main.py check      → فحص الإعدادات والتبعيات
"""

from __future__ import annotations

import argparse
import importlib
import logging
import subprocess
import sys
from pathlib import Path

from config import settings, AUTHOR, COPYRIGHT_NOTICE


def cmd_bot(args):
    from bot.telegram_bot import PixelZeroBaranBot
    bot = PixelZeroBaranBot()
    bot.run()


def cmd_dashboard(args):
    dashboard_path = Path(__file__).parent / "dashboard" / "streamlit_app.py"
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(dashboard_path), "--server.port=8501"],
        check=True,
    )


def cmd_pipeline(args):
    from scripts.run_pipeline import main as pipeline_main
    sys.argv = ["run_pipeline.py", args.image, "--style", args.style,
                "--desc", args.desc, "--size", str(args.size)]
    pipeline_main()


def cmd_batch(args):
    from scripts.batch_processor import main as batch_main
    sys.argv = ["batch_processor.py", str(args.input_dir), "--style", args.style,
                "--desc", args.desc, "--size", str(args.size), "--delay", str(args.delay)]
    if args.report:
        sys.argv += ["--report", str(args.report)]
    batch_main()


def cmd_info(args):
    print("=" * 60)
    print(f"🎨 {AUTHOR['project']} — v{AUTHOR['version']}")
    print("=" * 60)
    print(f"👤 المؤلف:    {AUTHOR['name']}")
    print(f"✉️ البريد:    {AUTHOR['email']}")
    print(f"📱 واتساب:    {AUTHOR['whatsapp']}")
    print(f"🏦 IBAN:      {AUTHOR['iban']}")
    print(f"📄 الترخيص:   {AUTHOR['license']}")
    print("=" * 60)
    print(COPYRIGHT_NOTICE)
    print("=" * 60)


def cmd_check(args):
    print("🔍 فحص الإعدادات والتبعيات...\n")

    # إعدادات
    errors = settings.validate()
    if errors:
        print("⚠️ تنبيهات الإعدادات:")
        for e in errors:
            print(f"   • {e}")
    else:
        print("✅ كل الإعدادات الحرجة متوفرة.")

    # تبعيات اختيارية
    deps = {
        "rembg": "إزالة الخلفية",
        "supabase": "التخزين السحابي",
        "streamlit": "لوحة التحكم",
        "requests": "اتصال الـ APIs",
        "PIL": "معالجة الصور الأساسية",
        "dotenv": "تحميل .env",
    }
    print("\n📦 حالة التبعيات:")
    for mod, role in deps.items():
        try:
            importlib.import_module(mod)
            print(f"   ✅ {mod:12s} — {role}")
        except ImportError:
            print(f"   ❌ {mod:12s} — {role}  (pip install {mod.lower().replace('pil','pillow')})")


def main():
    parser = argparse.ArgumentParser(
        prog="pixel-zerobaran",
        description="Pixel-ZeroBaran — المنظومة الذاتية الذكية للأصول البصرية",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("bot", help="تشغيل بوت تليجرام").set_defaults(func=cmd_bot)
    sub.add_parser("dashboard", help="تشغيل لوحة Streamlit").set_defaults(func=cmd_dashboard)

    p_pipe = sub.add_parser("pipeline", help="تشغيل pipeline على صورة واحدة")
    p_pipe.add_argument("image", type=str)
    p_pipe.add_argument("--style", default="studio_marble")
    p_pipe.add_argument("--desc", default="منتج فاخر")
    p_pipe.add_argument("--size", type=int, default=1024)
    p_pipe.set_defaults(func=cmd_pipeline)

    p_batch = sub.add_parser("batch", help="معالجة دفعة كاملة")
    p_batch.add_argument("input_dir", type=str)
    p_batch.add_argument("--style", default="studio_marble")
    p_batch.add_argument("--desc", default="منتج فاخر")
    p_batch.add_argument("--size", type=int, default=1024)
    p_batch.add_argument("--delay", type=float, default=2.0)
    p_batch.add_argument("--report", type=str, default=None)
    p_batch.set_defaults(func=cmd_batch)

    sub.add_parser("info", help="معلومات المؤلف وحقوق الملكية").set_defaults(func=cmd_info)
    sub.add_parser("check", help="فحص الإعدادات والتبعيات").set_defaults(func=cmd_check)

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    args.func(args)


if __name__ == "__main__":
    main()
