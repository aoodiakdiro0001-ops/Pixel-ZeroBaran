# 📋 CHANGELOG — Pixel-ZeroBaran

جميع التغييرات الجوهرية في كل إصدار.

الصيغة مبنية على [Keep a Changelog](https://keepachangelog.com/ar/1.1.0/)，
ورقم الإصدار يتبع [Semantic Versioning](https://semver.org/lang/ar/).

---

## [1.0.0] — 2026-10-31 🎉

أول إصدار رسمي وعمومي للمنظومة الذاتية الذكية لتوليد الأصول البصرية.

### ✨ Added — المُضاف

#### الطبقة الأساسية
- **`core/background_remover.py`** — عزل المنتجات عن خلفياتها باستخدام Rembg + نموذج u2net.
  - دعم `alpha-matting` لتنعيم الحواف.
  - شحذ تلقائي لقناة الألفا.
  - معالجة مجلدات كاملة دفعة واحدة.
- **`core/ai_generator.py`** — العقل التوليدي:
  - `HuggingFaceClient` للاتصال بنماذج Stable Diffusion (توليد خلفيات + inpainting).
  - `GeminiClient` لصياغة الأوصاف البصرية والنصوص الإعلانية بالعربية.
  - `AIVisualEngine` لدمج المنتج المعزول فوق الخلفية المولّدة مع ظل طبيعي.
- **`core/storage.py`** — طبقة التخزين:
  - `SupabaseStorage` لرفع الصور وتسجيل السجلات في PostgreSQL.
  - `LocalStorage` كـ fallback عند غياب Supabase.
  - إنشاء تلقائي لـ Buckets والجداول.

#### طبقة التوصيل
- **`bot/telegram_bot.py`** — بوت تليجرام كامل:
  - استلام صور + caption (وصف + هاشتاج النمط).
  - أوامر: `/start`, `/help`, `/about`, `/styles`.
  - إرسال النتيجة النهائية مع النص الإعلاني والهاشتاجات.
- **`dashboard/streamlit_app.py`** — لوحة تحكم ويب:
  - رفع الصور من المتصفح.
  - اختيار النمط والأبعاد من الشريط الجانبي.
  - عرض النتيجة + أزرار التحميل + سجل آخر الأصول.

#### الأنماط البصرية الجاهزة
- `studio_marble` — رخام فاخر مع إضاءة استوديو.
- `sunny_beach` — شاطئ مشمس بوقت ذهبي.
- `minimal_white` — خلفية بيضاء نقية للـ e-commerce.
- `luxury_dark` — استوديو داكن درامي سينمائي.
- `forest_nature` — غابة خضراء مع إضاءة متلألئة.

#### الأتمتة
- **`.github/workflows/cron-batch.yml`** — جدولة يومية لمعالجة الدفعات.
- **`scripts/run_pipeline.py`** — خط أنابيب موحّد CLI + Python API.
- **`scripts/batch_processor.py`** — معالج دفعات كاملة مع تقارير JSON.

#### التوثيق
- **`README.md`** — دليل شامل بالعربية.
- **`LICENSE`** — حقوق ملكية كاملة باسم Baran Avisat.
- **`docs/ARCHITECTURE.md`** — تفصيل البنية الهندسية.
- **`docs/DEPLOYMENT.md`** — دليل النشر الكامل (محلي + سحابي).
- **`docs/API_REFERENCE.md`** — مرجع كامل للـ API الداخلي.
- **`docs/supabase_schema.sql`** — مخطط قاعدة البيانات.
- **`AUTHORS.md`**, **`CONTRIBUTING.md`**, **`CHANGELOG.md`**.

#### الأدوات
- **`main.py`** — نقطة دخول موحّدة (bot/dashboard/pipeline/batch/info/check).
- **`tests/test_basic.py`** — اختبارات أساسية للإعدادات والمكونات.
- **`.env.example`** — قالب المتغيرات البيئية.

### 🏗️ Technical — التقني

- Python 3.10+ (مُختبَر على 3.11).
- تبعيات: Pillow, rembg, onnxruntime, supabase, streamlit, requests, python-dotenv, tqdm.
- كل التبعيات مجانية ومفتوحة المصدر.
- لا اعتماد على أي خدمة مدفوعة.

### 📊 Metrics — المقاييس

- وقت المعالجة المتوقع لصورة واحدة: 15-40 ثانية.
- التكلفة المتوقعة: 0.00$.
- حدود الطبقات المجانية:
  - Hugging Face: ~1000 inference/يوم.
  - Gemini: 15 req/min, 1500/يوم.
  - Supabase: 500MB تخزين.
  - GitHub Actions: 2000 دقيقة/شهر.

---

## [Unreleased] — قيد التطوير

### ✨ Planned — المُخطط

- [ ] دعم الفيديو القصير (Reels/TikTok) عبر توليد إطارات متتابعة.
- [ ] توليد كتالوج PDF تلقائي من الأصول المولّدة.
- [ ] واجهة عربية كاملة RTL للوحة Streamlit.
- [ ] دعم نماذج Flux المجانية على HuggingFace.
- [ ] ربط مباشر مع منصات التجارة الإلكترونية (Shopify/Salla/Zid).
- [ ] تطبيق Flutter للهواتف يستدعي نفس الـ API.
- [ ] نظام مصادقة متعدد المستخدمين.
- [ ] تكامل مع WhatsApp Cloud API بدل/إضافة لتليجرام.
- [ ] تخزين مؤقت ذكي لتجنب تكرار توليد نفس المشهد.

---

**© Baran Avisat — Pixel-ZeroBaran**
