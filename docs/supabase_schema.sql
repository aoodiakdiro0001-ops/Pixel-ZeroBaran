-- ============================================================
-- Pixel-ZeroBaran | مخطط قاعدة بيانات Supabase
-- المؤلف: Baran Avisat — Baranavisat@gmail.com
-- ============================================================
-- نفّذ هذا السكريبت من: Supabase Dashboard → SQL Editor

-- 1) جدول الأصول البصرية المولّدة
CREATE TABLE IF NOT EXISTS pixel_zerobaran_assets (
    id              BIGSERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    source          TEXT,                    -- telegram / streamlit / batch / cli
    raw_path        TEXT,                    -- URL أو مسار محلي للصورة الخام
    generated_path  TEXT,                    -- URL أو مسار الصورة الإعلانية النهائية
    scene_prompt    TEXT,                    -- الوصف البصري الذي صاغه Gemini
    style           TEXT,                    -- النمط المستخدم
    ad_caption      TEXT,                    -- النص الإعلاني
    ad_hashtags     TEXT[],                  -- الهاشتاجات
    elapsed_seconds NUMERIC,                 -- زمن المعالجة
    status          TEXT DEFAULT 'ok',       -- ok / error
    error           TEXT                     -- رسالة الخطأ إن وُجد
);

-- 2) فهرسة زمن الإنشاء للاستعلام السريع
CREATE INDEX IF NOT EXISTS idx_pixel_assets_created_at
    ON pixel_zerobaran_assets (created_at DESC);

-- 3) فهرسة الحالة
CREATE INDEX IF NOT EXISTS idx_pixel_assets_status
    ON pixel_zerobaran_assets (status);

-- 4) تفعيل Row Level Security (افتراضي آمن)
ALTER TABLE pixel_zerobaran_assets ENABLE ROW LEVEL SECURITY;

-- 5) سياسة: السماح بالقراءة والإدراج لكل من يملك المفتاح (anon + service)
CREATE POLICY "allow_all_pixel_assets" ON pixel_zerobaran_assets
    FOR ALL USING (true) WITH CHECK (true);

-- 6) Buckets التخزين (إنشاؤها تلقائياً من الكود أيضاً)
INSERT INTO storage.buckets (id, name, public)
VALUES ('pixel-raw', 'pixel-raw', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO storage.buckets (id, name, public)
VALUES ('pixel-generated', 'pixel-generated', true)
ON CONFLICT (id) DO NOTHING;

-- 7) سياسات التخزين العامة للقراءة والكتابة
CREATE POLICY "public_read_pixel_raw" ON storage.objects
    FOR SELECT USING (bucket_id = 'pixel-raw');

CREATE POLICY "public_write_pixel_raw" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'pixel-raw');

CREATE POLICY "public_read_pixel_generated" ON storage.objects
    FOR SELECT USING (bucket_id = 'pixel-generated');

CREATE POLICY "public_write_pixel_generated" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'pixel-generated');

-- ============================================================
-- انتهى المخطط — Pixel-ZeroBaran v1.0.0
-- ============================================================
