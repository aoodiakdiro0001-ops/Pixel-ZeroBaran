"""
Pixel-ZeroBaran | الطبقة الثالثة: الأرشيف والتخزين
====================================================
تتعامل مع Supabase Storage & PostgreSQL لحفظ الأصول البصرية
وسجلات الحملات.
"""

from __future__ import annotations

import io
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from config import settings

logger = logging.getLogger("pixel-zerobaran.storage")


# --------------------------------------------------------------------------- #
#  عميل Supabase                                                              #
# --------------------------------------------------------------------------- #
class SupabaseStorage:
    """ wrapper مبسّط لـ Supabase Storage + جدول بسيط للسجلات. """

    def __init__(self):
        try:
            from supabase import create_client, Client  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "حزمة supabase غير مثبتة — ثبّتها عبر: pip install supabase"
            ) from exc

        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError("إعدادات Supabase غير مضبوطة في .env")

        self.client: Client = create_client(
            settings.supabase_url, settings.supabase_key
        )
        self.bucket_raw = settings.supabase_bucket_raw
        self.bucket_generated = settings.supabase_bucket_generated
        self._ensure_buckets()
        self._ensure_tables()

    # ------------------------------------------------------------------ #
    def _ensure_buckets(self) -> None:
        """ينشئ الـ buckets إن لم تكن موجودة."""
        for name in (self.bucket_raw, self.bucket_generated):
            try:
                self.client.storage.get_bucket(name)
            except Exception:  # noqa: BLE001
                try:
                    self.client.storage.create_bucket(name, {"public": True})
                    logger.info("تم إنشاء bucket: %s", name)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("تعذّر إنشاء bucket %s: %s", name, exc)

    # ------------------------------------------------------------------ #
    def _ensure_tables(self) -> None:
        """ينشئ جدول السجلات إن لم يكن موجوداً (best-effort)."""
        ddl = """
        CREATE TABLE IF NOT EXISTS pixel_zerobaran_assets (
            id BIGSERIAL PRIMARY KEY,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            source TEXT,
            raw_path TEXT,
            generated_path TEXT,
            scene_prompt TEXT,
            style TEXT,
            ad_caption TEXT,
            ad_hashtags TEXT[],
            elapsed_seconds NUMERIC,
            status TEXT DEFAULT 'ok',
            error TEXT
        );
        """
        try:
            self.client.rpc("exec_sql", {"query": ddl}).execute()
        except Exception as exc:  # noqa: BLE001
            # RPC غير متاح افتراضياً — نسجل تحذير والمستخدم ينشئ الجدول يدوياً
            logger.warning(
                "تعذّر تنفيذ DDL تلقائياً (%s). أنشئ الجدول يدوياً من SQL Editor:", exc
            )
            logger.warning(ddl)

    # ------------------------------------------------------------------ #
    def upload_raw(self, image_bytes: bytes, filename: str) -> str:
        """يرفع صورة المنتج الخام ويرجع المسار العام."""
        path = f"raw/{int(time.time())}_{filename}"
        self.client.storage.from_(self.bucket_raw).upload(
            path, image_bytes, {"content-type": "image/png", "upsert": True}
        )
        public_url = self.client.storage.from_(self.bucket_raw).get_public_url(path)
        logger.info("رُفعت صورة خام: %s", public_url)
        return public_url

    # ------------------------------------------------------------------ #
    def upload_generated(self, image_bytes: bytes, filename: str) -> str:
        """يرفع الصورة الإعلانية النهائية ويرجع المسار العام."""
        path = f"generated/{int(time.time())}_{filename}"
        self.client.storage.from_(self.bucket_generated).upload(
            path, image_bytes, {"content-type": "image/jpeg", "upsert": True}
        )
        public_url = self.client.storage.from_(self.bucket_generated).get_public_url(path)
        logger.info("رُفعت صورة مولّدة: %s", public_url)
        return public_url

    # ------------------------------------------------------------------ #
    def log_asset(self, **kwargs: Any) -> None:
        """يسجل بيانات الأصل في جدول pixel_zerobaran_assets."""
        try:
            self.client.table("pixel_zerobaran_assets").insert(kwargs).execute()
            logger.info("تم تسجيل الأصل في قاعدة البيانات.")
        except Exception as exc:  # noqa: BLE001
            logger.warning("فشل تسجيل السجل: %s", exc)

    # ------------------------------------------------------------------ #
    def list_recent(self, limit: int = 20) -> list[dict]:
        """يرجع آخر N سجل."""
        try:
            resp = (
                self.client.table("pixel_zerobaran_assets")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return resp.data or []
        except Exception as exc:  # noqa: BLE001
            logger.warning("فشل جلب السجلات: %s", exc)
            return []


# --------------------------------------------------------------------------- #
#  Fallback محلي عند غياب Supabase                                            #
# --------------------------------------------------------------------------- #
class LocalStorage:
    """تخزين محلي بسيط يُستخدم عند غياب إعدادات Supabase."""

    def __init__(self):
        settings.ensure_dirs()
        self._db_path = settings.project_root / "assets" / "local_db.jsonl"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    def upload_raw(self, image_bytes: bytes, filename: str) -> str:
        import hashlib
        h = hashlib.md5(image_bytes).hexdigest()[:8]
        p = settings.raw_dir / f"{h}_{filename}"
        p.write_bytes(image_bytes)
        return str(p)

    def upload_generated(self, image_bytes: bytes, filename: str) -> str:
        import hashlib
        h = hashlib.md5(image_bytes).hexdigest()[:8]
        p = settings.output_dir / f"{h}_{filename}"
        p.write_bytes(image_bytes)
        return str(p)

    def log_asset(self, **kwargs: Any) -> None:
        import json
        kwargs["created_at"] = datetime.utcnow().isoformat()
        with self._db_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(kwargs, ensure_ascii=False) + "\n")

    def list_recent(self, limit: int = 20) -> list[dict]:
        import json
        if not self._db_path.exists():
            return []
        lines = self._db_path.read_text(encoding="utf-8").strip().splitlines()
        records = [json.loads(l) for l in lines if l]
        return records[-limit:][::-1]


# --------------------------------------------------------------------------- #
#  مصنع موحّد                                                                 #
# --------------------------------------------------------------------------- #
def get_storage():
    """يرجع عميل Supabase إن توفرت إعداداته، وإلا عميل محلي."""
    try:
        return SupabaseStorage()
    except Exception as exc:  # noqa: BLE001
        logger.info("التحويل إلى تخزين محلي: %s", exc)
        return LocalStorage()


__all__ = ["SupabaseStorage", "LocalStorage", "get_storage"]
