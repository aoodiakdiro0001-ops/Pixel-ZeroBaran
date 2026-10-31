# 🏗️ Pixel-ZeroBaran — البنية الهندسية

> تفصيل كامل لطبقات النظام، تدفق البيانات، والقرارات المعمارية.

---

## 🎯 المبادئ المعمارية

1. **الفصل بين الطبقات** — كل طبقة مسؤولة عن مهمة واحدة ويمكن استبدالها دون لمس البقية.
2. **التعافي التلقائي (Graceful Degradation)** — غياب Supabase يُحوّل للتخزين المحلي، غياب Gemini يستخدم fallback محلي، غياب HF يعطّل التوليد فقط دون انهيار النظام.
3. **موارد مجانية بالكامل** — لا اعتماد على أي خدمة مدفوعة إطلاقاً.
4. **قابلية الأتمتة** — كل مكون قابل للتشغيل من CLI أو من جدولة GitHub Actions.
5. **الملكية الكاملة للبيانات** — صور المنتجات تُخزّن في بيئة المستخدم الخاصة.

---

## 🔁 تدفق البيانات الكامل (End-to-End)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          المستخدم (User)                                │
│              يرسل صورة منتج عبر تليجرام أو يرفعها في الويب              │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              ④ طبقة التوصيل (Delivery Layer)                            │
│  ┌──────────────────────┐         ┌──────────────────────────────────┐  │
│  │  Telegram Bot API    │         │  Streamlit Dashboard             │  │
│  │  (bot/telegram_bot)  │         │  (dashboard/streamlit_app)       │  │
│  └──────────┬───────────┘         └──────────────┬───────────────────┘  │
│             │                                    │                      │
│             └──────────────┬─────────────────────┘                      │
└────────────────────────────┼────────────────────────────────────────────┘
                             │ image_bytes + description + style
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│          🎯 PixelZeroBaranPipeline (scripts/run_pipeline.py)            │
│                   — المنسّق الموحّد لكل الطبقات —                        │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────────┐
         ▼                   ▼                       ▼
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────────────────┐
│ ① Background    │ │ ② AIVisualEngine │ │ ③ Storage                   │
│   Remover       │ │                  │ │                             │
│ (Rembg + U2Net) │ │ GeminiClient →   │ │ SupabaseStorage or          │
│                 │ │   craft_prompt   │ │ LocalStorage                │
│ Input: raw JPG  │ │                  │ │                             │
│ Output: PNG     │ │ HuggingFace →    │ │ • upload_raw()              │
│   (RGBA)        │ │   generate_bg    │ │ • upload_generated()        │
│                 │ │                  │ │ • log_asset()               │
│                 │ │ composite →      │ │ • list_recent()             │
│                 │ │   product+bg     │ │                             │
│                 │ │                  │ │                             │
│                 │ │ GeminiClient →   │ │                             │
│                 │ │   write_ad_copy  │ │                             │
└────────┬────────┘ └────────┬─────────┘ └──────────────┬──────────────┘
         │                   │                          │
         └───────────────────┼──────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              ④ طبقة التوصيل (مرة أخرى — الرد)                           │
│  • Telegram Bot: sendPhoto + caption (نص إعلاني + هاشتاجات)             │
│  • Streamlit:    عرض الصورة + أزرار التحميل + السجل                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 تفصيل الطبقات

### ① طبقة المعالجة (`core/background_remover.py`)

**المسؤولية:** عزل المنتج عن خلفيته الأصلية بجودة عالية.

**التقنية:**
- مكتبة `rembg` مفتوحة المصدر.
- نموذج `u2net` (يُنزَّل مرة واحدة، ~176MB).
- خيار `alpha-matting` لتنعيم الحواف (أبطأ لكن أدق للشعر والحواف الناعمة).

**الواجهة:**
```python
remover = BackgroundRemover(model_name="u2net")
png_bytes, meta = remover.remove_background(image_bytes=raw_bytes)
# meta = {elapsed_seconds, model, alpha_matting, output_format, output_bytes}
```

**الأداء:** ~1-3 ثوانٍ للصورة (حسب حجمها وحسب GPU/CPU).

---

### ② طبقة التوليد (`core/ai_generator.py`)

ثلاثة كائنات:

**`GeminiClient`** — صياغة الأفكار:
```python
gemini = GeminiClient()
prompt = gemini.craft_scene_prompt("ساعة يد فاخرة", style="luxury_dark")
# → "luxury dark moody studio, dramatic rim lighting, premium steel watch..."
ad_copy = gemini.write_ad_copy("ساعة يد فاخرة")
# → {"caption": "⌚ الفخامة في كل تفصيل...", "hashtags": ["#ساعات", "#فخامة"]}
```

**`HuggingFaceClient`** — توليد الصور:
```python
hf = HuggingFaceClient()
bg_bytes = hf.generate_background(prompt=prompt, width=1024, height=1024)
# إعادة محاولة تلقائية عند 503 (النموذج قيد التحميل على البنية المجانية)
```

**`AIVisualEngine`** — المنسّق الموحّد:
```python
engine = AIVisualEngine()
result = engine.generate_ad(
    product_png_bytes=cutout_bytes,
    product_description="ساعة يد فاخرة",
    style="luxury_dark",
    size=(1024, 1024),
)
# result = {image_bytes, scene_prompt, ad_copy, meta}
```

الدمج يتم بإسقاط المنتج المعزول في وسط الخلفية المولّدة مع:
- ظل طبيعي (Gaussian blur على قناة الألفا).
- تحجيم المنتج إلى 70% من ارتفاع الخلفية مع الحفاظ على نسبته.

---

### ③ طبقة التخزين (`core/storage.py`)

**استراتيجية التعافي:**
```
get_storage() → يحاول SupabaseStorage → إن فشل → LocalStorage
```

**`SupabaseStorage`:**
- Buckets: `pixel-raw` (الخام), `pixel-generated` (المولّد).
- جدول `pixel_zerobaran_assets` (راجع `docs/supabase_schema.sql`).
- يُنشئ Buckets والجداول تلقائياً عند أول تشغيل (best-effort).

**`LocalStorage`** (fallback):
- يحفظ في `assets/raw/`, `assets/output/`.
- يسجل في `assets/local_db.jsonl` (JSON Lines).
- مفيد للتطوير المحلي بدون حساب Supabase.

---

### ④ طبقة التوصيل

**`bot/telegram_bot.py`:**
- long-polling مع `offset` متتبّع.
- يدعم الأوامر: `/start`, `/help`, `/about`, `/styles`.
- استلام صور + caption (الوصف + هاشتاج النمط).
- إرسال الصورة النهائية + النص الإعلاني + الهاشتاجات.
- تسجيل اسم المؤلف وحقوق الملكية في `/about`.

**`dashboard/streamlit_app.py`:**
- رفع صور من المتصفح.
- اختيار النمط + الوصف + الأبعاد من الشريط الجانبي.
- عرض المنتج المعزول + الإعلان النهائي + النص الإعلاني.
- زر تحميل مباشر.
- عرض آخر 6 أصول منفذة من `storage.list_recent()`.
- شريط تقدم حيّ أثناء المعالجة.

---

## 🔄 حالات الاستخدام

### الحالة 1: بوت تليجرام (الأساسية)
```
User → Telegram → Bot → Pipeline → Result back via Telegram
```

### الحالة 2: لوحة Streamlit محلية
```
User → Browser → Streamlit → Pipeline → Display in browser
```

### الحالة 3: معالجة دفعات مجدولة
```
GitHub Actions (cron) → batch_processor.py → Pipeline for each → Supabase
```

### الحالة 4: CLI للاختبار السريع
```
Developer → python main.py pipeline image.jpg → Console output
```

---

## 🛡️ الاستراتيجيات الدفاعية

| الخطر | الاستجابة |
|---|---|
| HF API 503 (نموذج يُحمَّل) | إعادة محاولة تلقائية مع `retry-after` |
| Gemini API فاشل | fallback محلي يبني وصفاً من القاموس الجاهز |
| Supabase غير مُعد | تحويل تلقائي إلى `LocalStorage` |
| rembg غير مثبت | رسالة خطأ واضحة مع أمر التثبيت |
| حجم صورة كبير | `Image.LANCZOS` resampling لتحجيم آمن |
| توكنات ناقصة | `settings.validate()` يرجع قائمة أخطاء واضحة |

---

## 📈 مقاييس الأداء المتوقعة

| المهمة | الوقت المتوقع | الحد المجاني |
|---|---|---|
| إزالة الخلفية | 1-3 ثوانٍ | غير محدود (محلي) |
| صياغة وصف Gemini | 1-2 ثانية | 15 طلب/دقيقة (مجاني) |
| توليد خلفية HF | 10-30 ثانية | ~1000 طلب/يوم (مجاني) |
| رفع Supabase | <1 ثانية | 500MB تخزين (مجاني) |
| **المجموع لصورة واحدة** | **~15-40 ثانية** | **0$** |

---

## 🔐 اعتبارات الأمان

- لا تُخزَّن التوكنات في الكود — كلها في `.env` (مستثنى من Git).
- GitHub Actions يأخذ الأسرار من `secrets` ولا تظهر في السجلات.
- Supabase RLS مفعّل على جدول الأصول.
- صور المستخدمين تُخزّن في buckets خاصة بهم، لا تُستخدم لتدريب نماذج خارجية.

---

**© Baran Avisat — Pixel-ZeroBaran v1.0.0**
