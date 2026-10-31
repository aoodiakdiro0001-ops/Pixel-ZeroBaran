"""
Pixel-ZeroBaran | طبقة التسليم والتوصيل
========================================
بوت تليجرام لاستلام صور المنتجات الخام وإرجاع الأصول الإعلانية الجاهزة.
"""

from __future__ import annotations

import io
import logging
import tempfile
from pathlib import Path

import requests
from PIL import Image

from config import settings, AUTHOR, COPYRIGHT_NOTICE
from core.background_remover import BackgroundRemover
from core.ai_generator import AIVisualEngine
from core.storage import get_storage

logger = logging.getLogger("pixel-zerobaran.telegram")


# --------------------------------------------------------------------------- #
class PixelZeroBaranBot:
    """بوت تليجرام كامل المزايا."""

    API_BASE = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self):
        if not settings.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN غير مضبوط في .env")
        self.token = settings.telegram_bot_token
        self.remover = BackgroundRemover()
        self.engine = AIVisualEngine()
        self.storage = get_storage()
        self._offset = 0
        self._commands = [
            ("start", "ابدأ واستعرض المزايا"),
            ("help", "شرح طريقة الاستخدام"),
            ("about", "معلومات المؤلف وحقوق الملكية"),
            ("styles", "عرض الأنماط البصرية المتاحة"),
        ]
        self._register_commands()

    # ------------------------------------------------------------------ #
    def _register_commands(self) -> None:
        """يسجّل قائمة الأوامر في تليجرام."""
        try:
            payload = {"commands": [{"command": c, "description": d} for c, d in self._commands]}
            requests.post(self.API_BASE.format(token=self.token) + "/setMyCommands", json=payload, timeout=10)
        except Exception as exc:  # noqa: BLE001
            logger.warning("تعذّر تسجيل الأوامر: %s", exc)

    # ------------------------------------------------------------------ #
    def send_message(self, chat_id: str, text: str, parse_mode: str = "Markdown") -> None:
        url = self.API_BASE.format(token=self.token) + "/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode}, timeout=30)

    # ------------------------------------------------------------------ #
    def send_photo(self, chat_id: str, image_bytes: bytes, caption: str = "") -> None:
        url = self.API_BASE.format(token=self.token) + "/sendPhoto"
        files = {"photo": ("ad.jpg", image_bytes, "image/jpeg")}
        data = {"chat_id": chat_id, "caption": caption[:1024]}
        requests.post(url, files=files, data=data, timeout=120)

    # ------------------------------------------------------------------ #
    def download_file(self, file_id: str) -> bytes:
        """ينزّل ملفاً من تليجرام باستخدام file_id."""
        url = self.API_BASE.format(token=self.token) + "/getFile"
        resp = requests.get(url, params={"file_id": file_id}, timeout=30)
        resp.raise_for_status()
        file_path = resp.json()["result"]["file_path"]
        dl_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        r = requests.get(dl_url, timeout=60)
        r.raise_for_status()
        return r.content

    # ------------------------------------------------------------------ #
    def run(self) -> None:
        """الحلقة الرئيسية للبوت (long-polling)."""
        logger.info("🤖 Pixel-ZeroBaran Bot يعمل الآن...")
        self._broadcast_started()

        while True:
            try:
                updates = self._get_updates()
                for update in updates:
                    self._handle_update(update)
            except KeyboardInterrupt:
                logger.info("تم إيقاف البوت يدوياً.")
                break
            except Exception as exc:  # noqa: BLE001
                logger.exception("خطأ غير متوقع: %s", exc)

    # ------------------------------------------------------------------ #
    def _broadcast_started(self) -> None:
        if settings.telegram_chat_id:
            self.send_message(
                settings.telegram_chat_id,
                f"🚀 *Pixel-ZeroBaran* بدأ التشغيل بنجاح!\n\n{COPYRIGHT_NOTICE}"
            )

    # ------------------------------------------------------------------ #
    def _get_updates(self) -> list:
        url = self.API_BASE.format(token=self.token) + "/getUpdates"
        resp = requests.post(url, json={"offset": self._offset, "timeout": 30}, timeout=60)
        resp.raise_for_status()
        data = resp.json().get("result", [])
        if data:
            self._offset = data[-1]["update_id"] + 1
        return data

    # ------------------------------------------------------------------ #
    def _handle_update(self, update: dict) -> None:
        message = update.get("message")
        if not message:
            return

        chat_id = str(message["chat"]["id"])
        text = (message.get("text") or "").strip()
        photo = message.get("photo")
        caption = (message.get("caption") or "").strip()

        try:
            if text.startswith("/start"):
                self._cmd_start(chat_id)
            elif text.startswith("/help"):
                self._cmd_help(chat_id)
            elif text.startswith("/about"):
                self._cmd_about(chat_id)
            elif text.startswith("/styles"):
                self._cmd_styles(chat_id)
            elif photo:
                # صورة + وصف اختياري في الـ caption
                self._process_photo(chat_id, photo, caption)
            else:
                self.send_message(
                    chat_id,
                    "📸 أرسل صورة منتج مع وصف اختياري، أو استخدم /help لعرض الأوامر."
                )
        except Exception as exc:  # noqa: BLE001
            logger.exception("خطأ في معالجة التحديث")
            self.send_message(chat_id, f"⚠️ حدث خطأ أثناء المعالجة: {exc}")

    # ------------------------------------------------------------------ #
    def _cmd_start(self, chat_id: str) -> None:
        self.send_message(
            chat_id,
            "*🎨 Pixel-ZeroBaran*\n"
            "المنظومة الذاتية الذكية لتوليد الأصول البصرية والإعلانات.\n\n"
            "📸 أرسل صورة منتجك الخام مع وصف بسيط، وسأعيدها لك "
            "كإعلان احترافي جاهز للنشر خلال ثوانٍ.\n\n"
            "اكتب /help لعرض كل المزايا."
        )

    # ------------------------------------------------------------------ #
    def _cmd_help(self, chat_id: str) -> None:
        self.send_message(
            chat_id,
            "*📖 طريقة الاستخدام*\n\n"
            "1️⃣ أرسل صورة المنتج الخام.\n"
            "2️⃣ اكتب وصفاً مختصراً في الـ caption "
            "(مثال: «زجاجة عطر فاخرة ذهبية»).\n"
            "3️⃣ اختر النمط بإضافة هاشتاق من القائمة:\n"
            "   `#studio_marble` `#sunny_beach` `#minimal_white` `#luxury_dark` `#forest_nature`\n"
            "4️⃣ انتظر بضع ثوانٍ — سيعود إليك الإعلان جاهزاً!\n\n"
            "/styles — عرض كل الأنماط\n"
            "/about — معلومات المؤلف"
        )

    # ------------------------------------------------------------------ #
    def _cmd_styles(self, chat_id: str) -> None:
        lines = ["*🎨 الأنماط البصرية المتاحة:*"]
        for key, desc in settings.scene_presets.items():
            lines.append(f"\n`#{key}`\n_{desc[:80]}…_")
        self.send_message(chat_id, "\n".join(lines))

    # ------------------------------------------------------------------ #
    def _cmd_about(self, chat_id: str) -> None:
        self.send_message(
            chat_id,
            f"*ℹ️ Pixel-ZeroBaran — v{AUTHOR['version']}*\n\n"
            f"👤 المؤلف: *{AUTHOR['name']}*\n"
            f"✉️ البريد: `{AUTHOR['email']}`\n"
            f"📱 واتساب: `{AUTHOR['whatsapp']}`\n\n"
            f"_{COPYRIGHT_NOTICE}_"
        )

    # ------------------------------------------------------------------ #
    def _process_photo(self, chat_id: str, photo_sizes: list, caption: str) -> None:
        # نختار أعلى جودة متاحة
        biggest = max(photo_sizes, key=lambda p: p.get("file_size", 0))
        self.send_message(chat_id, "⏳ جارٍ معالجة الصورة... قد تستغرق 30-60 ثانية.")

        # 1) تنزيل الصورة الأصلية
        raw_bytes = self.download_file(biggest["file_id"])
        self.storage.upload_raw(raw_bytes, f"chat_{chat_id}.jpg")

        # 2) استخراج النمط من الـ caption
        style = "studio_marble"
        for key in settings.scene_presets:
            if f"#{key}" in caption.lower():
                style = key
                break

        product_desc = caption.replace(f"#{style}", "").strip() or "منتج فاخر"

        # 3) إزالة الخلفية
        cutout_bytes, bg_meta = self.remover.remove_background(image_bytes=raw_bytes)

        # 4) توليد الإعلان
        result = self.engine.generate_ad(
            product_png_bytes=cutout_bytes,
            product_description=product_desc,
            style=style,
        )

        # 5) حفظ الناتج في التخزين
        generated_url = self.storage.upload_generated(
            result["image_bytes"], f"ad_{chat_id}.jpg"
        )

        # 6) تسجيل السجل
        self.storage.log_asset(
            source=f"telegram:{chat_id}",
            raw_path=f"chat_{chat_id}.jpg",
            generated_path=generated_url,
            scene_prompt=result["scene_prompt"],
            style=style,
            ad_caption=result["ad_copy"].get("caption", ""),
            ad_hashtags=result["ad_copy"].get("hashtags", []),
            elapsed_seconds=result["meta"]["elapsed_seconds"],
            status="ok",
        )

        # 7) إرسال النتيجة
        ad = result["ad_copy"]
        hashtags = " ".join(ad.get("hashtags", []))
        caption_out = (
            f"🎨 *تم إنجاز التصميم البصري بنجاح!*\n\n"
            f"🖼️ النمط: `{style}`\n"
            f"⏱️ استغرق: {result['meta']['elapsed_seconds']}s\n\n"
            f"📝 {ad.get('caption', '')}\n"
            f"{hashtags}\n\n"
            f"📥 الصورة جاهزة للتحميل والنشر المباشر."
        )
        self.send_photo(chat_id, result["image_bytes"], caption_out)


__all__ = ["PixelZeroBaranBot"]
