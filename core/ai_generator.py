"""
Pixel-ZeroBaran | الطبقة الثانية: العقل الإبداعي والتوليدي
============================================================
يربط النظام بنماذج Hugging Face المجانية و Google Gemini
لتوليد خلفيات إعلانية احترافية ودمج المنتجات فيها.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

import requests
from PIL import Image

from config import settings

logger = logging.getLogger("pixel-zerobaran.ai")


# --------------------------------------------------------------------------- #
#  عميل Hugging Face                                                          #
# --------------------------------------------------------------------------- #
class HuggingFaceClient:
    """عميل مبسّط لـ Hugging Face Inference API."""

    API_URL_TEMPLATE = "https://api-inference.huggingface.co/models/{model}"

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.hf_token
        if not self.token:
            logger.warning("HF_TOKEN غير مضبوط — التوليد عبر HuggingFace معطّل.")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    # ------------------------------------------------------------------ #
    def generate_background(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        model: Optional[str] = None,
        retries: int = 3,
    ) -> bytes:
        """
        يولّد صورة خلفية إعلانية من نص وصف.

        Args:
            prompt: وصف الخلفية المطلوبة.
            width, height: الأبعاد.
            model: اسم النموذج (افتراضي يأتي من الإعدادات).
            retries: عدد محاولات إعادة المحاولة عند فشل الطلب.

        Returns:
            بيانات الصورة بصيغة PNG.
        """
        model = model or settings.hf_model_bg
        url = self.API_URL_TEMPLATE.format(model=model)
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
            },
        }

        for attempt in range(1, retries + 1):
            logger.info("محاولة توليد %d/%d — النموذج: %s", attempt, retries, model)
            try:
                response = requests.post(
                    url, headers=self.headers, json=payload, timeout=90
                )
                if response.status_code == 200:
                    logger.info("تم توليد الخلفية بنجاح — %.1f KB",
                                len(response.content) / 1024)
                    return response.content
                if response.status_code == 503:
                    # النموذج قيد التحميل على البنية التحتية المجانية
                    wait = int(response.headers.get("retry-after", "20"))
                    logger.warning("النموذج قيد التحميل — انتظار %ss", wait)
                    time.sleep(wait)
                    continue
                logger.error("خطأ HF %s: %s", response.status_code, response.text[:300])
            except requests.RequestException as exc:
                logger.error("فشل الشبكة: %s", exc)
            time.sleep(3 * attempt)

        raise RuntimeError(f"فشل توليد الخلفية بعد {retries} محاولات.")

    # ------------------------------------------------------------------ #
    def inpaint_product_into_scene(
        self,
        product_png_bytes: bytes,
        scene_prompt: str,
        model: Optional[str] = None,
    ) -> bytes:
        """
        يدمج المنتج المعزول داخل مشهد مولّد باستخدام تقنية inpainting.

        يقوم بإنشاء قناع تلقائي بحجم الصورة ويُطلب من النموذج
        توليد خلفية متناسقة حول المنتج.
        """
        model = model or settings.hf_model_inpaint
        url = self.API_URL_TEMPLATE.format(model=model)

        # تجهيز صورة المنتج مع خلفية شفافة إلى RGB أبيض مؤقت
        product_img = Image.open(io.BytesIO(product_png_bytes)).convert("RGBA")
        if product_img.mode != "RGB":
            bg = Image.new("RGB", product_img.size, (255, 255, 255))
            bg.paste(product_img, mask=product_img.split()[-1])
            product_img = bg

        # بناء قناع يحدد منطقة المنتج (غير الأبيض)
        mask = Image.new("L", product_img.size, 255)
        # سنترك النموذج يعيد توليد كامل المشهد للحصول على اندماج طبيعي
        mask = Image.new("L", product_img.size, 0)

        # تحويل الصور إلى base64
        def img_to_b64(img: Image.Image, fmt: str = "PNG") -> str:
            buf = io.BytesIO()
            img.save(buf, format=fmt)
            return base64.b64encode(buf.getvalue()).decode()

        payload = {
            "inputs": {
                "image": img_to_b64(product_img),
                "mask": img_to_b64(mask),
                "prompt": scene_prompt,
            },
            "parameters": {"num_inference_steps": 30, "guidance_scale": 7.5},
        }

        response = requests.post(url, headers=self.headers, json=payload, timeout=120)
        if response.status_code != 200:
            raise RuntimeError(f"فشل inpainting: {response.status_code} {response.text[:300]}")
        return response.content


# --------------------------------------------------------------------------- #
#  عميل Google Gemini                                                         #
# --------------------------------------------------------------------------- #
class GeminiClient:
    """عميل مبسّط لـ Gemini API لصياغة الأفكار البصرية والنصوص الإعلانية."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            logger.warning("GEMINI_API_KEY غير مضبوط — صياغة الأفكار معطّلة.")

    # ------------------------------------------------------------------ #
    def craft_scene_prompt(self, product_description: str, style: str = "luxury") -> str:
        """
        يطلب من Gemini صياغة وصف بصري احترافي للمنتج.

        Args:
            product_description: وصف المنتج (مثال: "زجاجة عطر فاخرة ذهبية").
            style: النمط المطلوب (luxury / minimal / nature / dark / beach).

        Returns:
            وصف بصري جاهز لتمريره لنموذج التوليد.
        """
        if not self.api_key:
            #Fallback مبسّط بدون Gemini
            return self._fallback_prompt(product_description, style)

        url = f"{self.BASE_URL}/{settings.gemini_model}:generateContent?key={self.api_key}"
        system = (
            "You are a senior commercial advertising photographer and AI prompt engineer. "
            "Given a product description and a visual style, craft a single dense English "
            "prompt (max 60 words) for an image-generation model. The prompt MUST describe: "
            "1) lighting, 2) surface/material of the scene, 3) background, 4) mood, "
            "5) commercial advertising style, 6) '8k, ultra detailed'. "
            "Output ONLY the prompt, no explanation."
        )
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Product: {product_description}\nStyle: {style}"
                }]
            }],
            "systemInstruction": {"parts": [{"text": system}]},
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 200},
        }

        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            logger.info("Gemini صاغ وصفاً: %s", text[:80])
            return text
        except Exception as exc:  # noqa: BLE001
            logger.warning("فشل Gemini (%s) — استخدام fallback.", exc)
            return self._fallback_prompt(product_description, style)

    # ------------------------------------------------------------------ #
    def write_ad_copy(self, product_description: str, platform: str = "instagram") -> dict:
        """
        يولّد نصاً إعلانياً جاهزاً للنشر مع hashtags.
        """
        if not self.api_key:
            return {"caption": f"✨ {product_description} — متوفر الآن!", "hashtags": []}

        url = f"{self.BASE_URL}/{settings.gemini_model}:generateContent?key={self.api_key}"
        system = (
            "You are a senior Arabic-speaking social media copywriter. "
            "Given a product description and a platform, produce: "
            "1) a punchy caption in Arabic (2-3 lines), 2) 5 relevant Arabic+English hashtags. "
            "Return JSON with keys: caption, hashtags[]."
        )
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Product: {product_description}\nPlatform: {platform}"
                }]
            }],
            "systemInstruction": {"parts": [{"text": system}]},
            "generationConfig": {"temperature": 0.9, "maxOutputTokens": 300},
        }

        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            # محاولة parse JSON
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                # تنظيف بسيط
                cleaned = text.strip("`").replace("json\n", "")
                return json.loads(cleaned)
        except Exception as exc:  # noqa: BLE001
            logger.warning("فشل توليد النص الإعلاني: %s", exc)
            return {"caption": f"✨ {product_description} — اطلبه الآن!", "hashtags": []}

    # ------------------------------------------------------------------ #
    @staticmethod
    def _fallback_prompt(product: str, style: str) -> str:
        presets = settings.scene_presets
        base = presets.get(style, presets["studio_marble"])
        return f"{product}, {base}"


# --------------------------------------------------------------------------- #
#  المنسّق الموحّد                                                            #
# --------------------------------------------------------------------------- #
class AIVisualEngine:
    """
    يجمع عميل HuggingFace و Gemini في واجهة واحدة للاستخدام من قبل
    البوت ولوحة Streamlit وسكريبت الدفعات.
    """

    def __init__(self):
        self.hf = HuggingFaceClient()
        self.gemini = GeminiClient()

    # ------------------------------------------------------------------ #
    def generate_ad(
        self,
        product_png_bytes: bytes,
        product_description: str,
        style: str = "studio_marble",
        size: tuple[int, int] = (1024, 1024),
    ) -> dict:
        """
        يولّد صورة إعلانية كاملة.

        Returns:
            dict يحتوي على: image_bytes, scene_prompt, ad_copy, meta.
        """
        t0 = time.perf_counter()

        # 1) صياغة وصف المشهد عبر Gemini
        scene_prompt = self.gemini.craft_scene_prompt(product_description, style)
        logger.info("وصف المشهد: %s", scene_prompt)

        # 2) توليد خلفية المشهد
        bg_bytes = self.hf.generate_background(
            prompt=scene_prompt, width=size[0], height=size[1]
        )

        # 3) دمج المنتج المعزول فوق الخلفية المولّدة
        final_bytes = self._composite_product_on_background(
            product_png_bytes, bg_bytes, size
        )

        # 4) توليد النص الإعلاني المرافق
        ad_copy = self.gemini.write_ad_copy(product_description)

        elapsed = time.perf_counter() - t0
        return {
            "image_bytes": final_bytes,
            "scene_prompt": scene_prompt,
            "ad_copy": ad_copy,
            "meta": {
                "elapsed_seconds": round(elapsed, 2),
                "style": style,
                "size": size,
                "engine": "HuggingFace+Gemini",
            },
        }

    # ------------------------------------------------------------------ #
    @staticmethod
    def _composite_product_on_background(
        product_png_bytes: bytes, background_bytes: bytes, size: tuple[int, int]
    ) -> bytes:
        """يضع المنتج المعزول في وسط الخلفية المولّدة."""
        bg = Image.open(io.BytesIO(background_bytes)).convert("RGB").resize(size, Image.LANCZOS)
        product = Image.open(io.BytesIO(product_png_bytes)).convert("RGBA")

        # تحجيم المنتج ليناسب 70% من ارتفاع الخلفية مع الحفاظ على النسبة
        target_h = int(size[1] * 0.70)
        ratio = target_h / product.height
        new_w = int(product.width * ratio)
        product = product.resize((new_w, target_h), Image.LANCZOS)

        # إسقاط ظل خفيف أسفل المنتج
        from PIL import ImageFilter
        shadow = Image.new("RGBA", size, (0, 0, 0, 0))
        shadow_alpha = product.split()[-1].filter(ImageFilter.GaussianBlur(8))
        shadow_layer = Image.new("RGBA", size, (0, 0, 0, 0))
        shadow_layer.paste((0, 0, 0, 110), (0, 0), shadow_alpha)
        bg_rgba = bg.convert("RGBA")
        bg_rgba = Image.alpha_composite(bg_rgba, shadow_layer)

        # لصق المنتج في الوسط
        pos = ((size[0] - new_w) // 2, (size[1] - target_h) // 2)
        bg_rgba.paste(product, pos, product)

        out = io.BytesIO()
        bg_rgba.convert("RGB").save(out, format="JPEG", quality=settings.jpeg_quality)
        return out.getvalue()


__all__ = ["HuggingFaceClient", "GeminiClient", "AIVisualEngine"]
